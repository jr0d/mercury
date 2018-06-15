# Copyright 2015 Jared Rodriguez (jared.rodriguez@rackspace.com)
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import asyncio
import logging

import zmq
import zmq.asyncio

from mercury.common.asyncio.dispatcher import AsyncDispatcher
from mercury.common.asyncio.transport import TrivialAsyncRouterReqService
from mercury.common.asyncio.clients.inventory import \
    InventoryClient as AsyncInventoryClient
from mercury.common.clients.inventory import InventoryClient
from mercury.backend.active_asyncio import add_active_record, ping_loop, \
    stop_ping
from mercury.backend.controller import BackendController
from mercury.backend.options import parse_options
from mercury.backend.rpc_client import AsyncRPCClient

log = logging.getLogger(__name__)


class BackEndService(TrivialAsyncRouterReqService):
    def __init__(self,
                 bind_address,
                 inventory_client,
                 rpc_client,
                 name,
                 datacenter,
                 vip,
                 port):
        super(BackEndService, self).__init__(bind_address)

        self.inventory_client = inventory_client
        self.rpc_client = rpc_client
        self.server_info = {
            'name': name,
            'datacenter': datacenter,
            'address': vip,
            'port': port
        }
        self.controller = BackendController(self.server_info,
                                            self.inventory_client,
                                            self.rpc_client)

        self.dispatcher = AsyncDispatcher(self.controller)

    async def process(self, message):
        """ Process the message via dispatcher """
        return await self.dispatcher.dispatch(message)


def reacquire(inventory_url, backend_name):
    """

    :param inventory_url:
    :param backend_name:
    :return:
    """
    # Onetime use synchronous client
    log.info('Attempting to reacquire active agents')
    log.debug('Inventory Router: {}'.format(inventory_url))

    inventory_client = InventoryClient(inventory_url,
                                       # TODO: Add these to configuration
                                       response_timeout=60,
                                       rcv_retry=10)

    existing_documents = inventory_client.query({'active': {'$ne': None},
                                                 'origin.name': backend_name},
                                                projection={'mercury_id': 1,
                                                            'active': 1})

    if existing_documents.get('error'):  # Transport Error
        log.error('[BACKEND CRITICAL] '
                  'Error communicating with inventory service, could not '
                  'reacquire: <{}>'.format(existing_documents.get('message')))
        # Return without reacquiring any nodes. Once communication is
        # reestablished, agents will begin to re-register
        return

    for doc in existing_documents['message']['items']:
        if not BackendController.validate_agent_info(doc['active']):
            log.error('Found junk in document {} expunging'.format(
                doc['mercury_id']))
            inventory_client.update_one(doc['mercury_id'], {'active': None})

        log.info('Attempting to reacquire %s : %s' % (
            doc['mercury_id'], doc['active']['rpc_address']))
        add_active_record(doc)

    log.info('Reacquire operation complete')
    inventory_client.close()


def configure_logging(config):
    """ Configure logging for application
    :param config: A namespace provided from MercuryConfiguration.parse_args
    """
    logging.basicConfig(level=logging.getLevelName(config.logging.level),
                        format=config.logging.format)

    if config.subtask_debug:
        logging.getLogger('mercury.rpc.ping').setLevel(logging.DEBUG)
        logging.getLogger('mercury.rpc.ping2').setLevel(logging.DEBUG)
        logging.getLogger('mercury.rpc.jobs.monitor').setLevel(logging.DEBUG)

    if config.asyncio_debug:
        logging.getLogger('mercury.rpc.active_asyncio').setLevel(logging.DEBUG)


def main():
    """ Entry point """

    config = parse_options()

    configure_logging(config)

    # Create the event loop
    loop = zmq.asyncio.ZMQEventLoop()

    # If config.asyncio_debug == True, enable debug
    loop.set_debug(config.asyncio_debug)

    # Set the zmq event loop as the default event loop
    asyncio.set_event_loop(loop)

    # Create Async Clients
    inventory_client = AsyncInventoryClient(config.backend.inventory_router,
                                            linger=0,
                                            response_timeout=10,
                                            rcv_retry=3)
    rpc_client = AsyncRPCClient(config.backend.rpc_router,
                                linger=0,
                                response_timeout=10,
                                rcv_retry=3)

    # Create a backend instance
    server = BackEndService(config.backend.agent_service.bind_address,
                            inventory_client,
                            rpc_client,
                            config.backend.origin.name,
                            config.backend.origin.datacenter,
                            config.backend.origin.queue_service_vip,
                            config.backend.origin.queue_service_port)

    reacquire(config.backend.inventory_router, config.backend.origin.name)

    # Inject ping loop
    asyncio.ensure_future(ping_loop(
        server.context,
        config.backend.ping.interval,
        config.backend.ping.cycle_time,
        config.backend.ping.initial_timeout,
        config.backend.ping.retries,
        config.backend.ping.backoff,
        loop,
        config.backend.inventory_router),
        loop=loop)

    log.info('Starting Mercury Backend Service')
    try:
        loop.run_until_complete(server.start())
    except KeyboardInterrupt:
        # TODO: Add generic backend TERM handler
        log.info('Sending kill signals')
        stop_ping()
        server.kill()
    finally:
        pending = asyncio.Task.all_tasks(loop=loop)
        log.debug('Waiting on {} pending tasks'.format(len(pending)))
        loop.run_until_complete(asyncio.gather(*pending))
        log.debug('Shutting down event loop')
        loop.close()


if __name__ == '__main__':
    main()
