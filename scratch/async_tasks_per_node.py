import asyncio
import logging
import time

import msgpack
import zmq
import zmq.asyncio


log = logging.getLogger(__name__)


async def ping(mercury_id,
               ctx,
               zurl,
               cycle,
               retries,
               initial_timeout,
               backoff):
    while True:
        failures = 0
        while failures < retries:
            socket = ctx.socket(zmq.REQ)
            socket.setsockopt(zmq.LINGER, 0)
            socket.connect(zurl)
            payload = {
                'message': 'ping',
                'timestamp': time.time()
            }
            current_timeout = int((initial_timeout + (failures and initial_timeout or 0) * (failures**backoff)))
            log.debug('Pinging %s , payload: %s, timeout: %d' % (zurl, payload, current_timeout))
            await socket.send(msgpack.packb(payload))

            if await socket.poll(current_timeout):
                reply = await socket.recv()
                log.debug("ping success: %s : %s" % (zurl, msgpack.unpackb(reply, encoding='utf-8')))
                socket.close()
                break
            else:
                log.debug('ping timeout failures/backoff: {}/{}  : {} : {}'.format(
                    failures, backoff, mercury_id, zurl))
                failures += 1
                socket.close()
        if failures:
            return

        await asyncio.sleep(cycle)


def start_loop(loop):
    logging.basicConfig(level=logging.DEBUG)
    _ctx = zmq.asyncio.Context()
    loop = zmq.asyncio.ZMQEventLoop()
    loop.set_debug(True)
    asyncio.set_event_loop(loop)

    try:
        loop.run_forever()
    finally:
        loop.close()
        _ctx.destroy()


if __name__ == '__main__':
    import multiprocessing
    loop_process = multiprocessing.Process(target=start_loop)
    loop_process.start()

