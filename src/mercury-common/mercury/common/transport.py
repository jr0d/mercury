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

import logging
import msgpack
import zmq

from mercury.common.exceptions import (
    fancy_traceback_short,
    MercuryClientException,
    parse_exception
)

log = logging.getLogger(__name__)


def full_req_transceiver(zmq_url, data):
    """
    Used when you want to send and close

    :param zmq_url:
    :param data:
    :return:
    """
    # TODO: Harden this
    # TODO: Add linger and POLLIN support : https://github.com/zeromq/pyzmq/issues/132
    ctx, socket = get_ctx_and_connect_req_socket(zmq_url)

    packed = msgpack.packb(data)
    socket.send_multipart([packed])

    rep = socket.recv()
    unpacked_rep = msgpack.unpackb(rep, encoding='utf-8')

    socket.close()
    ctx.term()
    return unpacked_rep


def get_ctx_and_connect_req_socket(zmq_url):
    ctx = zmq.Context()
    # noinspection PyUnresolvedReferences
    socket = ctx.socket(zmq.REQ)
    socket.connect(zmq_url)

    return ctx, socket


class SimpleRouterReqClient(object):
    def __init__(self, zmq_url):
        self.zmq_url = zmq_url
        self.ctx, self.socket = get_ctx_and_connect_req_socket(self.zmq_url)

    def transceiver(self, payload):
        # TODO: Harden this
        # TODO: Add linger and POLLIN support :
        # https://github.com/zeromq/pyzmq/issues/132

        packed = msgpack.packb(payload)

        # blocks
        self.socket.send_multipart([packed])

        # blocks
        rep = self.socket.recv()

        return msgpack.unpackb(rep, encoding='utf-8')

    def close(self):
        self.socket.close()


def parse_multipart_message(message):
    if len(message) < 3:
        log.error('Recieved non-multipart message')
        return {}

    address_segment = message[:-1]
    data_segment = message[-1]

    return {'address': address_segment, 'message': data_segment}


def serialize_addresses(multipart_address):
    addresses = []
    for el in multipart_address:
        if el:
            addresses.append(el)

    return addresses


class SimpleRouterReqService(object):
    def __init__(self, bind_address):
        self.bind_address = bind_address
        self.context = zmq.Context()
        # noinspection PyUnresolvedReferences
        self.socket = self.context.socket(zmq.ROUTER)
        self.bound = False

    def bind(self):
        self.socket.bind(self.bind_address)
        log.info('Bound: %s' % self.bind_address)
        self.bound = True

    def receive(self):
        multipart = self.socket.recv_multipart()

        parsed_message = parse_multipart_message(multipart)

        if not parsed_message:
            return

        try:
            message = msgpack.unpackb(parsed_message['message'], encoding='utf-8')
        except TypeError as type_error:
            self.send_error(parsed_message['address'], 'Recieved unpacked, non-string type: %s : %s' % (type(packed_message), type_error))
            return
        except msgpack.UnpackException as unpack_exception:
            self.send_error(parsed_message['address'], 'Received invalid request: %s' % str(unpack_exception))
            return

        return parsed_message['address'], message

    def send_error(self, address, message):
        data = {'error': True, 'message': message}
        log.error(message)
        self.send(address, data)

    def send(self, address, message):
        self.socket.send_multipart(address + [msgpack.packb(message)])

    def destroy(self):
        self.context.destroy()

    @staticmethod
    def get_key(key, data):
        try:
            return data[key]
        except KeyError:
            raise MercuryClientException('{} is missing from request'.format(key))

    @staticmethod
    def validate_required(required, data):
        missing = []
        for key in required:
            if key not in data:
                missing.append(data)

        if missing:
            raise MercuryClientException('Message is missing required data: {}'.format(missing))

    def start(self):
        if not self.bound:
            self.bind()

        while True:
            response = None
            try:
                data = self.receive()
            except KeyboardInterrupt:
                break
            if not data:
                continue
            address, message = data
            # log.debug('Request: %s' % binascii.hexlify(address))
            # noinspection PyBroadException
            try:
                response = self.process(message)
            except MercuryClientException as mce:
                self.send_error(address, 'Encountered client error: {}'.format(mce))
            except Exception:
                exec_dict = parse_exception()
                log.error('process raised an exception and should not have.')
                log.error(fancy_traceback_short(exec_dict))
                self.send_error(address, 'Encountered server error, sorry')
                continue
            # log.debug('Response: %s' % binascii.hexlify(address))
            self.send(address, response)
        self.cleanup()

    def process(self, message):
        raise NotImplementedError

    def cleanup(self):
        """
        override for more cleanup fun
        :return:
        """
        self.destroy()
