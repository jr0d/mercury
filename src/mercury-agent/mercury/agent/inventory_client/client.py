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

from mercury.common.exceptions import MercuryCritical
from mercury.common.transport import get_ctx_and_connect_req_socket


LOG = logging.getLogger(__name__)


class InventoryClient(object):
    def __init__(self, zmq_url):
        self.zmq_url = zmq_url
        self.ctx, self.socket = get_ctx_and_connect_req_socket(self.zmq_url)

    def transceiver(self, payload):
        LOG.debug('Transmitting payload')
        packed = msgpack.packb(payload)

        # blocks
        self.socket.send_multipart([packed])

        # blocks
        rep = self.socket.recv()

        return msgpack.unpackb(rep)

    @staticmethod
    def raise_reply_error(reply):
        raise MercuryCritical('Problem talking to inventory service: message = %s, tb = %s' % (
            reply.get('message'),
            '\n'.join(reply.get('tb', []))
        ))

    def check_and_return(self, reply):
        if reply.get('error'):
            self.raise_reply_error(reply)

        return reply['response']

    def update(self, update_data):
        if 'mercury_id' not in update_data:
            raise MercuryCritical('mercury_id is missing from payload')

        payload = {
            'endpoint': 'update',
            'args': [update_data]
        }

        return self.check_and_return(self.transceiver(payload))

    def get_one(self, mercury_id, projection=None):
        payload = {
            'endpoint': 'get_one',
            'args': [mercury_id],
            'kwargs': {
                'projection': projection
            }
        }
        return self.check_and_return(self.transceiver(payload))

    def query(self, query_data):
        payload = {
            'endpoint': 'query',
            'args': [query_data]
        }
        return self.check_and_return(self.transceiver(payload))

    def delete(self, mercury_id):
        payload = {
            'endpoint': 'delete',
            'args': [mercury_id]
        }
        return self.check_and_return(self.transceiver(payload))


if __name__ == '__main__':
    ic = InventoryClient('tcp://localhost:9000')
    _payload = {
                'mercury_id': 12345,
                'attribute1': 'I am a pickle',
                'attribute2': 'I hate pickles'
               }
    print ic.update(_payload)
    print ic.get_one(12345, projection={'mercury_id': 1})
    print ic.query({'attribute2': 'I hate pickles'})
    print ic.delete(12345)
