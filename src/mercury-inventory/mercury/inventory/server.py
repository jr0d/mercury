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
from mercury.common.log import log_format
from mercury.inventory.controller import InventoryController
from mercury.inventory.configuration import get_inventory_configuration

log = logging.getLogger(__name__)


class InventoryServer(transport.AsyncRouterReqService):
    def __init__(self, bind_address, inventory_configuration):
        super(InventoryServer, self).__init__(bind_address)

        inventory_controller = InventoryController(inventory_configuration)
        self.dispatcher = dispatcher.AsyncDispatcher(inventory_controller)

    async def process(self, message):
        return await self.dispatcher.dispatch(message)


def main(bind_address='tcp://0.0.0.0:9000',
         log_level='INFO',
         asyncio_debug=False,
         configuration_file=None):
    logging.basicConfig(level=logging.getLevelName(log_level),
                        format=log_format)

    loop = zmq.asyncio.ZMQEventLoop()
    loop.set_debug(asyncio_debug)
    asyncio.set_event_loop(loop)

    inventory_configuration = get_inventory_configuration(configuration_file)

    s = InventoryServer(bind_address=bind_address,
                        inventory_configuration=inventory_configuration)

    try:
        loop.run_until_complete(s.start())
    except KeyboardInterrupt:
        pass
    finally:
        s.socket.close(0)
        s.context.destroy()


if __name__ == '__main__':
    main()
