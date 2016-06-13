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


log = logging.getLogger(__name__)


RETRIES = 5  # TODO: YAML
PING_TIMEOUT = 2500  # TODO: YAML
BACK_OFF = .42

# make Lock a context manager
# make a lock decorator


class Lock(object):
    # TODO: Implement dead-lock detection
    def __init__(self):
        self.lock = threading.Lock()

    def acquire(self):
        log.debug('Lock acquired')
        return self.lock.acquire(True)  # block on acquire

    def release(self):
        log.debug('Lock released')
        self.lock.release()


class ActiveDBSyncList(object):
    TICKER = .02

    def __init__(self, db_controller, expire=5):
        self.__data = []
        self.lock = Lock()
        self.db_controller = db_controller
        self.load_time = 0
        self.expire = expire

    def append(self, last_ping, element):
        self.__data.append((
            last_ping,
            time.time(),
            element['mercury_id'],
            element['rpc_address'],
            element['rpc_address6'],
            element['ping_port']
        ))

    def load(self):
        self.lock.acquire()
        projection = {'mercury_id': 1,
                      'rpc_address': 1,
                      'rpc_address6': 1,
                      'ping_port': 1,
                      'time_created': 1}

        query = {'time_created': {'$gt': self.load_time}}

        cursor = self.db_controller(query=query, projection=projection)

        num_items = cursor.count()
        if num_items:
            log.debug('Loaded %d items from the database' % num_items)
            for element in cursor:
                self.append(0, element)

        self.lock.release()

    def sort(self):
        self.lock.acquire()
        now = time.time()
        self.__data.sort(key=lambda d: now - d[0])
        self.lock.release()

    def pop_expired(self):
        element = None
        self.lock.acquire()
        if self.__data:
            now = time.time()
            if now - self.__data[-1][0]:
                element = self.__data.pop()

        self.lock.release()
        return element


def ping(ctx, zurl, timeout=2500):
    _payload = {
        'message': 'ping',
        'timestamp': time.time()
    }
    socket = ctx.socket(zmq.REQ)
    socket.connect(zurl)

    log.debug('Pinging %s , payload: %s, timeout: %d' % (zurl, _payload, timeout))
    socket.send(msgpack.packb(_payload))

    if not socket.poll(timeout):
        log.debug('Ping timeout: %s' % zurl)
        socket.close()
        return False

    reply = socket.recv()
    log.debug("%s : %s" % (zurl, msgpack.unpackb(reply)))
    socket.close()
    return True
