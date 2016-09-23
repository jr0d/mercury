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

from pprint import pprint


def transceiver(s, d):
    packed = msgpack.packb(d)
    s.send_multipart([packed])
    return msgpack.unpackb(socket.recv(), encoding='utf-8')


def full_req_transceiver(zmq_url, data):
    ctx = zmq.Context()
    socket = ctx.socket(zmq.REQ)
    socket.connect(zmq_url)

    packed = msgpack.packb(data)
    socket.send_multipart([packed])

    rep = socket.recv()
    unpacked_rep = msgpack.unpackb(rep, encoding='utf-8')

    socket.close()

    return unpacked_rep


db_url = 'tcp://localhost:9000'
ctx = zmq.Context()
socket = ctx.socket(zmq.REQ)
socket.connect('tcp://localhost:9000')

# CREATE
payload = dict(
        endpoint='insert',
        args=[{
                'mercury_id': 12345,
                'attribute1': 'I am a pickle',
                'attribute2': 'I hate pickles'
               }]
        )

print(transceiver(socket, payload))
# pprint(full_req_transceiver(db_url, payload))

# GET
payload = dict(
    endpoint='get_one',
    args=[12345],
    kwargs={'projection': {'attribute2': 1, 'mercury_id': 1}}
)

print(transceiver(socket, payload))
# pprint(full_req_transceiver(db_url, payload))

# QUERY
payload = dict(
    endpoint='query',
    args=[{'attribute2': 'I hate pickles'}]
)

print(transceiver(socket, payload))
# pprint(full_req_transceiver(db_url, payload))

# DELETE
payload = dict(
    endpoint='delete',
    args=[12345]
)

pprint(transceiver(socket, payload))
# pprint(full_req_transceiver(db_url, payload))
