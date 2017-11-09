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

from mercury.rpc.frontend.controller import FrontEndController
from mercury.rpc.frontend.options import parse_options
from mercury.rpc.mongo import RPCCollectionFactory


log = logging.getLogger(__name__)


class FrontEndService(AsyncRouterReqService):
    """
    Front facing ZeroMQ service used for injecting RPC jobs
    """

    def __init__(self, bind_address,
                 inventory_router_url,
                 jobs_collection,
                 tasks_collection,
                 tasks_queue):
        """
        :param bind_address: ZeroMQ bind address
        :param inventory_router_url: ZeroMQ URL of Inventory router service
        :param jobs_collection: motor mongodb collection
        :param tasks_collection: motor mongodb collection
        :param tasks_queue: The task queue we are using
        """
        super(FrontEndService, self).__init__(bind_address)

        self.jobs_collection = jobs_collection
        self.tasks_collection = tasks_collection
        self.tasks_queue = tasks_queue
        self.controller = FrontEndController(inventory_router_url,
                                             jobs_collection,
                                             tasks_collection,
                                             tasks_queue)

        self.dispatcher = AsyncDispatcher(self.controller)

    async def process(self, message):
        return await self.dispatcher.dispatch(message)


def configure_logging(config):
    logging.basicConfig(level=logging.getLevelName(config.log_level),
                        format=config.log_format)
    if config.asyncio_debug:
        logging.getLogger('mercury.rpc.active_asyncio').setLevel(logging.DEBUG)


def rpc_frontend_service():
    """ Entry Point """

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

    server = FrontEndService(config.rpc.frontend.bind_address,
                             config.rpc.inventory_router,
                             collections.jobs_collection,
                             collections.tasks_collection,
                             config.rpc.redis.queue)

    # Start main loop
    log.info('Starting Mercury Frontend Service')
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
