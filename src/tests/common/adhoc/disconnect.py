import asyncio
import logging

import zmq.asyncio

from mercury.common.asyncio.transport import AsyncRouterReqService


log = logging.getLogger('disconnect')

logging.basicConfig(level=logging.DEBUG)


class WorkService(AsyncRouterReqService):
    async def process(self, message):
        if message['action'] == 'sleep':
            await asyncio.sleep(15)
            log.debug('Slept')
            return {'message': 'I slept'}
        if message['action'] == 'fast':
            log.debug('Fast')
            return {'message': 'I was fast'}
        if message['action'] == 'self-destruct':
            for i in reversed(range(6)):
                log.info('Self-destructing in t-minus {} seconds'.format(i))
                await asyncio.sleep(1)
            raise Exception('Have a nice day!')


loop = zmq.asyncio.ZMQEventLoop()
# loop = asyncio.get_event_loop()
loop.set_debug(True)

asyncio.set_event_loop(loop)

service = WorkService('tcp://0.0.0.0:9090', linger=0)

try:
    loop.run_until_complete(service.start())
except KeyboardInterrupt:
    log.info('Shutting down')
    service.kill()
finally:
    pending = asyncio.Task.all_tasks(loop=loop)
    log.debug('Waiting on {} pending tasks'.format(len(pending)))
    loop.run_until_complete(asyncio.gather(*pending))
    log.debug('Shutting down event loop')
    loop.close()
