import logging
import msgpack
import threading
import time
import zmq


RETRIES = 3
PING_TIMEOUT = 2500

log = logging.getLogger(__name__)


def ping(socket, host):
    socket.connect(host)

    poll = zmq.Poller()
    poll.register(socket, zmq.POLLIN)

    retries_left = RETRIES

    success = False
    while retries_left:
        _payload = {
            'message': 'ping',
            'timestamp': time.time()
        }
        socket.send(msgpack.packb(_payload))
        socks = dict(poll.poll(PING_TIMEOUT))
        if socks.get(socket) == zmq.POLLIN:
            reply = socket.recv()
            log.debug("%s : %s" % (host, reply))
            success = True
            break
        log.debug('timeout')
        retries_left -= retries_left
        time.sleep(5)
        socket.connect(host)
        poll.register(socket, zmq.POLLIN)
    return success


def pinger(server, mercury_id, db_controller):
    ctx = zmq.Context.instance()
    socket = ctx.socket(zmq.REQ)
    while True:
        log.debug('Pinging %s : %s' % (mercury_id, server))
        result = ping(socket, server)
        if not result:
            break
        time.sleep(5)

    log.info('%s : %s ping timeout' % (mercury_id, server))
    db_controller.remove(mercury_id)


def spawn(server, mercury_id, db_controller):
    thread = threading.Thread(target=pinger, args=[server, mercury_id, db_controller])
    log.info('Spawning pinger thread: %s : %s' % (mercury_id, server))
    thread.start()

