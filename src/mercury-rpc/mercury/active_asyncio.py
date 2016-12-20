import asyncio
import logging
import time

import msgpack
import zmq
import zmq.asyncio

log = logging.getLogger(__name__)
ping_queue = asyncio.Queue()


async def ping(ctx, timeout=2, count=0):
    socket = ctx.socket(zmq.REQ)
    socket.connect('tcp://0.0.0.0:9004')
    payload = {
        'message': 'ping',
        'timestamp': time.time()
    }
    socket.send(msgpack.packb(payload))
    if not await socket.poll(timeout=timeout*1000):
        log.debug('ping timeout')
        return False

    message = await socket.recv()
    log.debug(msgpack.unpackb(message, encoding='utf-8'))


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    _ctx = zmq.asyncio.Context()
    loop = zmq.asyncio.ZMQEventLoop()
    asyncio.set_event_loop(loop)

    loop.run_until_complete(ping(_ctx))
    loop.close()

