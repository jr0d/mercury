# Copyright 2017 Jared Rodriguez (jared.rodriguez@rackspace.com)
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

from mercury.common.asyncio.mongo import get_connection
from mercury.common.asyncio.transport import AsyncRouterReqService
from mercury.common.asyncio.dispatcher import AsyncDispatcher
from mercury.rpc.configuration import rpc_configuration, get_jobs_collection, get_tasks_collection
from mercury.rpc.frontend.controller import FrontEndController

log = logging.getLogger(__name__)


class FrontEndService(AsyncRouterReqService):
    """
    Front facing ZeroMQ service used for injecting RPC jobs
    """

    def __init__(self, inventory_client, jobs_collection, tasks_collection):
        """

        :param jobs_collection: motor mongodb collection
        :param tasks_collection: motor mongodb collection
        """
        service_bind_address = rpc_configuration.get('frontend',
                                                     {}).get('service_url',
                                                             'tcp://0.0.0.0:9001')
        super(FrontEndService, self).__init__(service_bind_address)

        self.inventory_client = inventory_client
        self.jobs_collection = jobs_collection
        self.tasks_collection = tasks_collection

        self.controller = FrontEndController(inventory_client,
                                             jobs_collection,
                                             tasks_collection)

        self.dispatcher = AsyncDispatcher(self.controller)

    async def process(self, message):
        return await self.dispatcher.dispatch(message)


def rpc_frontend_service():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s : %(levelname)s - %(name)s - %(message)s')

    db_configuration = rpc_configuration.get('db', {})

    # Create the event loop
    loop = zmq.asyncio.ZMQEventLoop()
    loop.set_debug(True)
    asyncio.set_event_loop(loop)

    # Ready the DB
    connection = get_connection(server_or_servers=db_configuration.get('rpc_mongo_servers',
                                                                       'localhost'),
                                replica_set=db_configuration.get('replica_set'))

    jobs_collection = get_jobs_collection(connection)
    tasks_collection = get_tasks_collection(connection)

    jobs_collection.create_index('ttl_time_completed', expireAfterSeconds=3600)
    tasks_collection.create_index('ttl_time_completed', expireAfterSeconds=3600)

    inventory_router = rpc_configuration['inventory']['inventory_router']

    server = FrontEndService(inventory_router, jobs_collection, tasks_collection)

    # Start main loop
    try:
        loop.run_until_complete(server.start())
    except KeyboardInterrupt:
        log.info('Stopping services')
        server.kill()
    finally:
        pending = asyncio.Task.all_tasks(loop=loop)
        loop.run_until_complete(asyncio.gather(*pending))
        loop.close()


if __name__ == '__main__':
    rpc_frontend_service()
