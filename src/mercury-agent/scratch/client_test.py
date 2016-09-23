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

import msgpack
import zmq


def transceiver(s, d):
    packed = msgpack.packb(d)
    s.send_multipart([packed])
    return msgpack.unpackb(socket.recv(), encoding='utf-8')


ctx = zmq.Context()
socket = ctx.socket(zmq.REQ)
socket.connect('tcp://localhost:9003')

for i in range(100):
    response = transceiver(socket, dict(category='rpc', method='echo', args=['This is the message: %s' % i]))
    print(response)


response = transceiver(socket, dict(category='rpc', method='inspector'))

from pprint import pprint
pprint(response)
