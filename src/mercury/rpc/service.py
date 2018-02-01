import asyncio
import logging

import zmq.asyncio

from mercury.common.asyncio.clients.inventory import InventoryClient
from mercury.common.asyncio import transport, dispatcher

from mercury.rpc.controller import RPCController
from mercury.rpc.jobs.monitor import Monitor
from mercury.rpc.mongo import init_rpc_collections
from mercury.rpc.options import parse_options


log = logging.getLogger(__name__)


class RPCService(transport.AsyncRouterReqService):
    def __init__(self,
                 bind_address,
                 inventory_client,
                 jobs_collection,
                 tasks_collection):
        """

        :param bind_address:
        :param inventory_client:
        :param jobs_collection:
        :param tasks_collection:
        """
        super(RPCService, self).__init__(bind_address)
        controller = RPCController(inventory_client,
                                   jobs_collection,
                                   tasks_collection)
        self.dispatcher = dispatcher.AsyncDispatcher(controller)

    async def process(self, message):
        return await self.dispatcher.dispatch(message)


def configure_logging(config):
    """ Configure logging for application
    :param config: A namespace provided from MercuryConfiguration.parse_args
    """
    logging.basicConfig(level=logging.getLevelName(config.logging.level),
                        format=config.logging.format)

    if config.subtask_debug:
        logging.getLogger('mercury.rpc.jobs.monitor').setLevel(logging.DEBUG)


def main():
    config = parse_options()

    configure_logging(config)

    # Configure the event loop
    loop = zmq.asyncio.ZMQEventLoop()
    loop.set_debug(config.asyncio_debug)
    asyncio.set_event_loop(loop)

    # Ready the DB
    collections = init_rpc_collections(
        servers=config.rpc.database.servers,
        database=config.rpc.database.name,
        jobs_collection=config.rpc.database.jobs_collection,
        tasks_collection=config.rpc.database.tasks_collection,
        replica_name=config.rpc.database.replica_name,
        username=config.rpc.database.username,
        password=config.rpc.database.password,
        use_asyncio=True
    )

    # Create an inventory socket
    inventory_client = InventoryClient(
        config.rpc.inventory_router,
        # TODO: add these values to the configuration
        linger=10,
        response_timeout=5,
        rcv_retry=3
    )

    # Add TTL indexes for completed jobs/tasks
    collections.jobs_collection.create_index('ttl_time_completed',
                                             expireAfterSeconds=3600)
    collections.tasks_collection.create_index('ttl_time_completed',
                                              expireAfterSeconds=3600)

    # Inject the monitor onto the event loop
    monitor = Monitor(collections.jobs_collection, collections.tasks_collection,
                      loop=loop)
    asyncio.ensure_future(monitor.loop(), loop=loop)

    service = RPCService(config.rpc.bind_address,
                         inventory_client,
                         collections.jobs_collection,
                         collections.tasks_collection)

    log.info('Starting Mercury Backend Service')
    try:
        loop.run_until_complete(service.start())
    except KeyboardInterrupt:
        # TODO: Add generic backend TERM handler
        log.info('Sending kill signals')
        monitor.kill()
        service.kill()
    finally:
        pending = asyncio.Task.all_tasks(loop=loop)
        log.debug('Waiting on {} pending tasks'.format(len(pending)))
        loop.run_until_complete(asyncio.gather(*pending))
        log.debug('Shutting down event loop')
        loop.close()


if __name__ == '__main__':
    main()
