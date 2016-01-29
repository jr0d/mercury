"""
rpc service handshake:

    registration service starts
    client connects and sends hostname and agent rpc services ports
    server adds device to active queue and spawns a ping worker
    while a device is active, the task manager will monitor the command queue of the device (stored
    in the active device record)
    the task manager will process the queue and assign a job to an available worker

    ping:

    client connects to registration service
    server will ping client
    when ping fails, server will un-register the client

"""
import threading
import time
import zmq

server_host = 'tcp://0.0.0.0:10001'
client_port_range = (12000, 13999)

RETRIES = 3
PING_TIMEOUT = 2500


def ping(socket, host):
    socket.connect(host)

    poll = zmq.Poller()
    poll.register(socket, zmq.POLLIN)

    retries_left = RETRIES

    success = False
    while retries_left:
        socket.send('ping')
        socks = dict(poll.poll(PING_TIMEOUT))
        if socks.get(socket) == zmq.POLLIN:
            reply = socket.recv()
            print "I: reply: %s" % reply
            success = True
            break
        print "Timeout"
        retries_left -= retries_left
        time.sleep(5)
        socket.connect(host)
        poll.register(socket, zmq.POLLIN)
        socket.send('ping')
    return success


def pinger():
    ctx = zmq.Context.instance()
    socket = ctx.socket(zmq.REQ)
    while True:
        print 'I: sending ping'
        result = ping(socket, server_host)
        print result
        time.sleep(10)


def pong(socket):
    """
    client side
    :return:
    """

    while True:
        r = socket.recv()
        if r == 'ping':
            socket.send('pong')


if __name__ == '__main__':
    ctx = zmq.Context(1)
    server = ctx.socket(zmq.REP)
    server.bind(server_host)

    server_thread = threading.Thread(target=pong, args=[server])
    server_thread.start()

    for x in xrange(1000):
        print 'I: Starting thread #%d' % x
        client_thread = threading.Thread(target=pinger)
        client_thread.start()
        time.sleep(.2)

    server_thread.join()
