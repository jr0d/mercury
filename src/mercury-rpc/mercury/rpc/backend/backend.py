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
from mercury.common.asyncio.mongo import get_connection
from mercury.common.asyncio.transport import AsyncRouterReqService
from mercury.common.asyncio.clients.inventory import InventoryClient as AsyncInventoryClient
from mercury.common.clients.inventory import InventoryClient
from mercury.rpc.active_asyncio import add_active_record, ping_loop, stop_ping
from mercury.rpc.backend.controller import BackendController
from mercury.rpc.configuration import rpc_configuration, get_jobs_collection, get_tasks_collection
from mercury.rpc.jobs.monitor import Monitor

log = logging.getLogger(__name__)

RPC_CONFIG_FILE = 'mercury-rpc.yaml'


class BackEndService(AsyncRouterReqService):

    def __init__(self, inventory_router_url, jobs_collection, tasks_collection):
        registration_service_bind_address = rpc_configuration.get('backend',
                                                                  {}).get('service_url',
                                                                          'tcp://0.0.0.0:9002')
        service_info = rpc_configuration.get('info', {})
        super(BackEndService, self).__init__(registration_service_bind_address)

        self.inventory_router_url = inventory_router_url
        self.inventory_client = AsyncInventoryClient(inventory_router_url)
        self.jobs_collection = jobs_collection
        self.tasks_collection = tasks_collection

        self.controller = BackendController(service_info,
                                            self.inventory_client,
                                            self.jobs_collection,
                                            self.tasks_collection)

        self.dispatcher = AsyncDispatcher(self.controller)

    async def process(self, message):
        """
        :param message:
        :return:
        """
        return await self.dispatcher.dispatch(message)

    def reacquire(self):

        # Onetime use synchronous client
        inventory_client = InventoryClient(self.inventory_router_url)

        existing_documents = inventory_client.query({'active': {'$ne': None}},
                                                    projection={'mercury_id': 1, 'active': 1})
        for doc in existing_documents['items']:
            if not self.controller.validate_agent_info(doc['active']):
                log.error('Found junk in document {} expunging'.format(doc['mercury_id']))
                inventory_client.update_one(doc['mercury_id'], {'active': None})

            log.info('Attempting to reacquire %s : %s' % (doc['mercury_id'], doc['active']['rpc_address']))
            add_active_record(doc)

        inventory_client.close()


def configure_logging():
    # TODO: get these from the configuration
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s : %(levelname)s - %(name)s - %(message)s')
    logging.getLogger('mercury.rpc.ping').setLevel(logging.INFO)
    logging.getLogger('mercury.rpc.ping2').setLevel(logging.INFO)
    logging.getLogger('mercury.rpc.jobs.monitor').setLevel(logging.INFO)
    logging.getLogger('mercury.rpc.active_asyncio').setLevel(logging.INFO)


def rpc_backend_service():
    """
    Entry point

    :return:
    """

    configure_logging()
    db_configuration = rpc_configuration.get('db', {})

    # Create the event loop
    loop = zmq.asyncio.ZMQEventLoop()
    loop.set_debug(False)
    asyncio.set_event_loop(loop)

    # Ready the DB
    connection = get_connection(server_or_servers=db_configuration.get('rpc_mongo_servers',
                                                                       'localhost'),
                                replica_set=db_configuration.get('replica_set'))

    jobs_collection = get_jobs_collection(connection)
    tasks_collection = get_tasks_collection(connection)

    jobs_collection.create_index('ttl_time_completed', expireAfterSeconds=3600)
    tasks_collection.create_index('ttl_time_completed', expireAfterSeconds=3600)

    # Inject the monitor loop
    monitor = Monitor(jobs_collection, tasks_collection, loop=loop)
    asyncio.ensure_future(monitor.loop(), loop=loop)

    # Create a backend instance
    inventory_router = rpc_configuration['inventory']['inventory_router']
    server = BackEndService(inventory_router, jobs_collection, tasks_collection)
    server.reacquire()

    # Inject ping loop
    asyncio.ensure_future(ping_loop(
        server.context, 30, 10, 2500, 5, .42, loop, inventory_router), loop=loop)

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
