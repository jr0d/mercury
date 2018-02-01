import asyncio
import logging
import zmq.asyncio

from mercury.common.asyncio import dispatcher, transport
from mercury.common.asyncio.mongo import get_connection as get_async_connection
from mercury.common.mongo import get_collection
from mercury.inventory.options import parse_options
from mercury.inventory.controller import InventoryController

log = logging.getLogger(__name__)


class InventoryServer(transport.AsyncRouterReqService):
    def __init__(self, bind_address, inventory_collection):
        super(InventoryServer, self).__init__(bind_address)

        inventory_controller = InventoryController(inventory_collection)
        self.dispatcher = dispatcher.AsyncDispatcher(inventory_controller)

    async def process(self, message):
        return await self.dispatcher.dispatch(message)


def main():
    config = parse_options()

    logging.basicConfig(level=logging.getLevelName(config.logging.level),
                        format=config.logging.format)

    loop = zmq.asyncio.ZMQEventLoop()
    loop.set_debug(config.asyncio_debug)
    asyncio.set_event_loop(loop)

    async_connection = get_async_connection(
        config.inventory.database.servers,
        config.inventory.database.replica_name,
        username=config.inventory.database.username,
        password=config.inventory.database.password
    )
    inventory_collection = get_collection(
        config.inventory.database.name,
        config.inventory.database.collection,
        connection=async_connection
    )

    s = InventoryServer(bind_address=config.inventory.bind_address,
                        inventory_collection=inventory_collection)

    try:
        loop.run_until_complete(s.start())
    except KeyboardInterrupt:
        log.info('Stopping service')
        s.kill()
    finally:
        pending = asyncio.Task.all_tasks(loop=loop)
        log.debug('Waiting on {} pending tasks'.format(len(pending)))
        loop.run_until_complete(asyncio.gather(*pending))
        log.debug('Shutting down event loop')
        loop.close()


if __name__ == '__main__':
    main()
