import asyncio
import logging
from concurrent.futures.thread import ThreadPoolExecutor

import redis
import zmq.asyncio

from mercury.common.asyncio.dispatcher import AsyncDispatcher
from mercury.common.asyncio.endpoints import (
    async_endpoint, StaticEndpointController
)
from mercury.common.asyncio.transport import AsyncRouterReqService

log = logging.getLogger(__name__)


class QueueServiceController(StaticEndpointController):
    """Simple Controller that will queue RPC tasks"""

    REQUIRED_TASK_KEYS = ['host', 'port', 'task_id', 'job_id', 'method', 'args',
                          'kwargs']

    def __init__(self, redis_client, queue_name, executor, loop):
        """

        :param redis_client:
        :param queue_name:
        :param executor:
        :param loop:
        """
        self.redis_client = redis_client
        self.queue_name = queue_name
        self.executor = executor
        self.loop = loop
        super(QueueServiceController, self).__init__()

    @async_endpoint('enqueue_task')
    async def enqueue_task(self, task):
        """

        :param task:
        :return:
        """
        self.validate_required(self.REQUIRED_TASK_KEYS, task)
        log.info('Enqueuing task: {job_id} / {task_id}'.format(**task))
        f = asyncio.wrap_future(
            self.executor.submit(self.redis_client.lpush,
                                 self.queue_name, task), loop=self.loop)

        await asyncio.wait_for(f, None, loop=self.loop)


class QueueService(AsyncRouterReqService):
    """ Simple backend for queueing jobs """
    def __init__(self, bind_address, redis_client, queue_name, loop=None,
                 executor_threads=10):
        """

        :param bind_address:
        :param redis_client:
        :param queue_name:
        :param loop:
        """
        super(QueueService, self).__init__(bind_address, loop=loop)
        executor = ThreadPoolExecutor(max_workers=executor_threads)
        controller = QueueServiceController(redis_client,
                                            queue_name,
                                            executor,
                                            self.loop)

        self.dispatcher = AsyncDispatcher(controller)

    async def process(self, message):
        return await self.dispatcher.dispatch(message)


def main():
    logging.basicConfig(level=logging.DEBUG)

    loop = zmq.asyncio.ZMQEventLoop()
    asyncio.set_event_loop(loop)
    server = QueueService('tcp://0.0.0.0:9002', redis.Redis(),
                           'rpc_task_queue', loop=loop)

    # Start main loop
    log.info('Starting Mercury Queue Service')
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
    main()
