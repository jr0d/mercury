import asyncio
import logging
import time

import msgpack
import zmq
import zmq.asyncio

log = logging.getLogger(__name__)

active_state = {}


async def ping(record, ctx, timeout, retries, backoff):
    """
    ping node until it responds or encounters x timeouts of x*backoff
    :param timeout:
    :param backoff:
    :param retries:
    :param record:
    :param ctx:
    :return:
    """
    failures = 0

    zurl = 'tcp://{}:{}'.format(record['rpc_address6'] or record['rpc_address'],
                                record['ping_port'])

    while failures < retries:
        socket = ctx.socket(zmq.REQ)
        socket.setsockopt(zmq.LINGER, 0)
        socket.connect(zurl)
        log.debug(socket)
        payload = {
            'message': 'ping',
            'timestamp': time.time()
        }
        current_timeout = int((timeout + (failures and timeout or 0) * (failures**backoff)))
        log.debug('Pinging %s , payload: %s, timeout: %d' % (zurl, payload, current_timeout))

        await socket.send(msgpack.packb(payload))

        if await socket.poll(current_timeout):  # Success condition
            # TODO: Do something with the payload, it contains the device load average
            # mayhaps put it in the active record and stuff it back into the database?

            reply = await socket.recv()  # Data is ready for snarfing

            log.debug("ping success: %s : %s" % (zurl, msgpack.unpackb(reply, encoding='utf-8')))
            socket.close()

            active_state[record['mercury_id']]['last_ping'] = time.time()
            active_state[record['mercury_id']]['pinging'] = False
            return

        log.debug('ping timeout failures/backoff: {}/{}  : {} : {}'.format(
            failures, backoff, record['mercury_id'], zurl))

        failures += 1

        socket.close()

    log.debug('Ping Failed! <REMOVE>')
    del active_state[record['mercury_id']]


async def ping_loop(ctx,
                    ping_interval,
                    cycle_time,
                    initial_ping_timeout,
                    ping_retries,
                    backoff,
                    loop):
    """

    :param ctx:
    :param ping_interval:
    :param cycle_time:
    :param initial_ping_timeout:
    :param ping_retries:
    :param backoff:
    :param loop:
    :return:
    """
    # load the queue
    while True:
        log.debug('looking for work')
        now = time.time()
        for mercury_id, data in list(active_state.items()):  # copy to list because the list length could change
            # out from under us
            if now - data['last_ping'] > ping_interval and not data['pinging']:
                log.debug('Scheduling ping for {}'.format(mercury_id))
                active_state[mercury_id]['pinging'] = True

                asyncio.ensure_future(ping(data, ctx, initial_ping_timeout, ping_retries, backoff),
                                      loop=loop)
        print('Before Sleep')
        await asyncio.sleep(cycle_time)
        print('After sleep')


if __name__ == '__main__':
    def load_shit(items=100):
        for i in range(items):
            active_state.update(
                {
                    str(i): {
                        'mercury_id': str(i),
                        'rpc_address': '0.0.0.0',
                        'ping_port': '9004',
                        'rpc_address6': None,
                        'last_ping': 0,
                        'pinging': False
                    }
                }
            )

    logging.basicConfig(level=logging.DEBUG)
    load_shit(10)
    _ctx = zmq.asyncio.Context()
    loop = zmq.asyncio.ZMQEventLoop()
    loop.set_debug(True)
    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(ping_loop(_ctx, 30, 10, 2500, 5, .42, loop))
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()
        _ctx.destroy()
