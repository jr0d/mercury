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
from mercury.common.asyncio.transport import AsyncRouterReqService
from mercury.common.asyncio.clients.inventory import \
    InventoryClient as AsyncInventoryClient
from mercury.common.clients.inventory import InventoryClient
from mercury.rpc.active_asyncio import add_active_record, ping_loop, stop_ping
from mercury.rpc.backend.controller import BackendController
from mercury.rpc.mongo import RPCCollectionFactory
from mercury.rpc.backend.options import parse_options
from mercury.rpc.jobs.monitor import Monitor

log = logging.getLogger(__name__)

RPC_CONFIG_FILE = 'mercury-rpc.yaml'


class BackEndService(AsyncRouterReqService):
    def __init__(self,
                 config,
                 jobs_collection,
                 tasks_collection):
        super(BackEndService, self).__init__(config.rpc.backend.bind_address)

        self.inventory_router_url = config.rpc.inventory_router
        self.inventory_client = AsyncInventoryClient(self.inventory_router_url)
        self.jobs_collection = jobs_collection
        self.tasks_collection = tasks_collection

        server_info = {
            'name': config.rpc.origin.name,
            'datacenter': config.rpc.origin.datacenter,
            'address': config.rpc.origin.public_address,
            'frontend_port': config.rpc.origin.frontend_port
        }
        self.controller = BackendController(server_info,
                                            self.inventory_client,
                                            self.jobs_collection,
                                            self.tasks_collection)

        self.dispatcher = AsyncDispatcher(self.controller)

    async def process(self, message):
        """ Process the message via dispatcher """
        return await self.dispatcher.dispatch(message)

    def reacquire(self):

        # Onetime use synchronous client
        inventory_client = InventoryClient(self.inventory_router_url)

        existing_documents = inventory_client.query({'active': {'$ne': None}},
                                                    projection={'mercury_id': 1,
                                                                'active': 1})
        for doc in existing_documents['items']:
            if not self.controller.validate_agent_info(doc['active']):
                log.error('Found junk in document {} expunging'.format(
                    doc['mercury_id']))
                inventory_client.update_one(doc['mercury_id'], {'active': None})

            log.info('Attempting to reacquire %s : %s' % (
            doc['mercury_id'], doc['active']['rpc_address']))
            add_active_record(doc)

        inventory_client.close()


def configure_logging(config):
    """ Configure logging for application
    :param config: A namespace provided from MercuryConfiguration.parse_args
    """
    logging.basicConfig(level=logging.getLevelName(config.log_level),
                        format=config.log_format)

    if config.subtask_debug:
        logging.getLogger('mercury.rpc.ping').setLevel(logging.DEBUG)
        logging.getLogger('mercury.rpc.ping2').setLevel(logging.DEBUG)
        logging.getLogger('mercury.rpc.jobs.monitor').setLevel(logging.DEBUG)

    if config.asyncio_debug:
        logging.getLogger('mercury.rpc.active_asyncio').setLevel(logging.DEBUG)


def rpc_backend_service():
    """ Entry point """

    config = parse_options()

    configure_logging(config)

    # Create the event loop
    loop = zmq.asyncio.ZMQEventLoop()

    # If config.asyncio_debug == True, enable debug
    loop.set_debug(config.asyncio_debug)

    # Set the zmq event loop as the default event loop
    asyncio.set_event_loop(loop)

    # Ready the DB

    collections = RPCCollectionFactory(
        servers=config.rpc.db.servers,
        database=config.rpc.db.name,
        jobs_collection=config.rpc.db.jobs_collection,
        tasks_collection=config.rpc.db.tasks_collection,
        replica_name=config.rpc.db.replica_name,
        use_asyncio=True
    )

    # Add TTL indexes for completed jobs/tasks
    collections.jobs_collection.create_index('ttl_time_completed',
                                             expireAfterSeconds=3600)
    collections.tasks_collection.create_index('ttl_time_completed',
                                              expireAfterSeconds=3600)

    # Inject the monitor loop
    monitor = Monitor(collections.jobs_collection, collections.tasks_collection,
                      loop=loop)
    asyncio.ensure_future(monitor.loop(), loop=loop)

    # Create a backend instance
    server = BackEndService(config,
                            collections.jobs_collection,
                            collections.tasks_collection)
    server.reacquire()

    # Inject ping loop
    asyncio.ensure_future(ping_loop(
        server.context,
        config.rpc.ping.interval,
        config.rpc.ping.cycle_time,
        config.rpc.ping.initial_timeout,
        config.rpc.ping.retries,
        config.rpc.ping.backoff,
        loop,
        config.rpc.inventory_router),
        loop=loop)

    log.info('Starting Mercury Backend Service')
    try:
        loop.run_until_complete(server.start())
    except KeyboardInterrupt:
        # TODO: Add generic service TERM handler
        log.info('Sending kill signals')
        monitor.kill()
        stop_ping()
        server.kill()
    finally:
        pending = asyncio.Task.all_tasks(loop=loop)
        loop.run_until_complete(asyncio.gather(*pending))
        loop.close()


if __name__ == '__main__':
    rpc_backend_service()
