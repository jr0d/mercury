# Copyright 2015 Jared Rodriguez (jared.rodriguez@rackspace.com)
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

"""
ping / pong payload

{timestamp: 1234567890.12345, message: 'ping'}
{timestamp: 1234567890.12345, load: (m, m5, m15}, message: 'pong'}
"""
import logging
import msgpack
import os
import multiprocessing
import time
import zmq


LOG = logging.getLogger(__name__)


class PongService(object):
    def __init__(self, bind_address):
        self.bind_address = bind_address
        self.ctx = zmq.Context()
        self.socket = self.ctx.socket(zmq.REP)
        self.running = False

    def bind(self):
        LOG.info('Binding pong service: %s' % self.bind_address)
        self.socket.bind(self.bind_address)

    @staticmethod
    def validate(message):
        keys = ['timestamp', 'message']
        for k in keys:
            if k not in message:
                return False
        if message['message'] != 'ping':
            return False

        return True

    def receive(self):
        r = self.socket.recv()

        try:
            message = msgpack.unpackb(r, encoding='utf-8')
        except TypeError as type_error:
            LOG.error('Recieved unpacked, non-string type: %s : %s' % (type(r), type_error))
            return
        except msgpack.UnpackException as unpack_exception:
            LOG.error('Received invalid request: %s' % str(unpack_exception))
            return

        if not self.validate(message):
            LOG.error('Received invalid request: %s' % message)
            return

        LOG.debug('Ping received: %s' % message)

        return message

    def pong(self):
        try:
            loadavg = os.getloadavg()
        except OSError as os_error:
            # Issue: https://github.com/jr0d/mercury/issues/4
            LOG.error('Error getting load average: %s' % str(os_error))
            loadavg = (0.0, 0.0, 0.0)

        _packet = {
            'timestamp': time.time(),
            'load': loadavg,
            'message': 'pong'
        }
        LOG.debug('PONG: %s' % _packet)
        # Could lock up here if server died immediately after sending ping
        # TODO: Lets test to find out what happens ^^
        self.socket.send(msgpack.packb(_packet))

    def run(self):
        while True:
            r = self.receive()
            if not r:
                continue

            self.pong()


def _spawn(bind_address):
    ping_service = PongService(bind_address)
    ping_service.bind()
    try:
        ping_service.run()
    except KeyboardInterrupt:
        pass


def spawn_pong_process(bind_address):
    p = multiprocessing.Process(target=_spawn, args=[bind_address])
    p.start()
    LOG.debug('pong service started: PID=%s' % p.pid)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    ps = PongService('tcp://0.0.0.0:9004')
    ps.bind()
    ps.run()
