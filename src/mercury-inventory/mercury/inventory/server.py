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
import zmq.asyncio

from mercury.common.asyncio import dispatcher, transport
from mercury.inventory.controller import InventoryController
from mercury.inventory.configuration import get_inventory_configuration

log = logging.getLogger(__name__)


class InventoryServer(transport.AsyncRouterReqService):
    def __init__(self, bind_address, config):
        super(InventoryServer, self).__init__(bind_address)

        inventory_controller = InventoryController(
            config.inventory.db.servers,
            config.inventory.db.replica_name,
            config.inventory.db.name,
            config.inventory.db.collection)

        self.dispatcher = dispatcher.AsyncDispatcher(inventory_controller)

    async def process(self, message):
        return await self.dispatcher.dispatch(message)


def main():
    config = get_inventory_configuration()

    logging.basicConfig(level=logging.getLevelName(config.log_level),
                        format=config.log_format)

    loop = zmq.asyncio.ZMQEventLoop()
    loop.set_debug(config.asyncio_debug)
    asyncio.set_event_loop(loop)

    s = InventoryServer(bind_address=config.inventory.bind_address,
                        config=config)

    try:
        loop.run_until_complete(s.start())
    except KeyboardInterrupt:
        log.info('Stopping service')
        s.kill()
    finally:
        pending = asyncio.Task.all_tasks(loop=loop)
        loop.run_until_complete(asyncio.gather(*pending))
        loop.close()


if __name__ == '__main__':
    main()
