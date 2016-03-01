# Copyright 2015 Jared Rodriguez (jared at blacknode dot net)
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

import logging
import msgpack
import threading
import time
import zmq


RETRIES = 3  # TODO: YAML
PING_TIMEOUT = 2500  # TODO: YAML

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
            log.debug("%s : %s" % (host, msgpack.unpackb(reply)))
            success = True
            break
        log.debug('timeout')
        retries_left -= retries_left
        time.sleep(5)  # TODO: YAML
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
        time.sleep(5)  # TODO: YAML
    # Scan jobs for any tasks targeting this node
    #  1. Fail the task
    #  2. Signal to any active worker threads to stop processing the task
    log.info('%s : %s ping timeout' % (mercury_id, server))
    db_controller.delete(mercury_id)


def spawn(server, mercury_id, db_controller):
    thread = threading.Thread(target=pinger, args=[server, mercury_id, db_controller])
    log.info('Spawning pinger thread: %s : %s' % (mercury_id, server))
    thread.start()

