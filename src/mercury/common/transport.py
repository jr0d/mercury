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
    """Used to send data and close connection.

    :param zmq_url: URL for the socket to connect to.
    :param data: The data to send.
    :returns: The unpacked response.
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
    """Creates a ZMQ context and a REQ socket.

    :param zmq_url: URL for the socket to connect to.
    :returns: A tuple containing the ZMQ context and the socket.
    """
    ctx = zmq.Context()
    # noinspection PyUnresolvedReferences
    socket = ctx.socket(zmq.REQ)
    socket.connect(zmq_url)

    return ctx, socket


class SimpleRouterReqClient(object):
    service_name = 'Generic router'

    def __init__(self, zmq_url, linger=-1, response_timeout=0):
        self.zmq_url = zmq_url
        self.ctx, self.socket = get_ctx_and_connect_req_socket(self.zmq_url)

        self.socket.setsockopt(zmq.LINGER, linger)
        self.poller = zmq.Poller()
        self.poller.register(self.socket, flags=zmq.POLLIN)
        self.response_timeout = response_timeout

    def raise_reply_error(self, reply):
        """Raise a MercuryCritical exception.

        Called when the client cannot talk to the inventory backend.
        :raises: MercuryClientException.
        """
        raise MercuryClientException(
            'Problem talking to {} backend: message = {}, tb = {}'.format(
                self.service_name,
                reply.get('message'),
                '\n'.join(reply.get('tb', []))
            ))

    def check_and_return(self, reply):
        """Check a transceiver's reply for errors.

        :param reply: A dictionary containing the transceiver's reply.
        :returns: The 'response' field of the transceiver's reply.
        """
        if isinstance(reply, dict):
            if reply.get('error'):
                self.raise_reply_error(reply)
            return reply.get('message') or reply.get('response')
        else:
            return reply

    def transceiver(self, payload):
        """Sends and receives messages.

        :param payload: A dict representing the message to send.
        :returns: A string representing the unpacked response.
        """
        # TODO: Harden this
        # TODO: Add linger and POLLIN support :
        # https://github.com/zeromq/pyzmq/issues/132

        packed = msgpack.packb(payload)

        # blocks
        self.socket.send_multipart([packed])

        if self.response_timeout:
            if not self.poller.poll(self.response_timeout * 1000):
                raise IOError('Timeout while waiting for server response')
        # blocks
        rep = self.socket.recv()

        return self.check_and_return(msgpack.unpackb(rep, encoding='utf-8'))

    def close(self):
        self.socket.close()


def parse_multipart_message(message):
    """Parses a ZMQ multipart message.

    Expected format of received message: ['address', '', 'data']

    :param message: The multipart message.
    :returns: A dict containing the 'address' and 'message' parts
        of the multipart message, or an empty dict.
    """
    if len(message) < 3:
        log.error('Received non-multipart message')
        return {}

    address_segment = message[:-1]
    data_segment = message[-1]

    return {'address': address_segment, 'message': data_segment}


def serialize_addresses(multipart_address):
    """Get the addresses from the address segment of a multipart message.

    :param multipart_address: A list representing the address part of a
        multipart message (including an empty delimiter).
    :returns: The list of non-empty addresses.
    """
    return [x for x in multipart_address if x]


def format_zurl(host, port, proto='tcp'):
    return f"{proto}://{host}:{port}"


class SimpleRouterReqService(object):
    """Base class for a message router backend."""

    def __init__(self, bind_address, linger=-1, poll_timeout=2):
        self.bind_address = bind_address
        self.context = zmq.Context()
        self.poll_timeout = poll_timeout
        self.socket = self.context.socket(zmq.ROUTER)
        self.socket.setsockopt(zmq.LINGER, linger)

        self.in_poller = zmq.Poller()
        self.in_poller.register(self.socket, zmq.POLLIN)

        log.info('Bound to: ' + self.bind_address)

        self.socket.bind(self.bind_address)

        self._kill = False

    def receive(self):
        multipart = self.socket.recv_multipart()
        parsed_message = parse_multipart_message(multipart)

        if not parsed_message:
            log.error('Received junk off the wire')
            raise MercuryClientException('Message is malformed')

        try:
            message = msgpack.unpackb(parsed_message['message'],
                                      encoding='utf-8')
        except TypeError as type_error:
            log.error('Received unpacked, non-string type: %s : %s' % (
                type(parsed_message), type_error))
            self.send_error(parsed_message['address'],
                            'Client error, message is not packed')
            raise MercuryClientException('Message is malformed')

        except (
                msgpack.UnpackException,
                msgpack.ExtraData) as msgpack_exception:
            log.error('Received invalid request: %s' % str(
                msgpack_exception))

            self.send_error(parsed_message['address'],
                            'Client error, message is malformed')
            raise MercuryClientException('Message is malformed')

        return parsed_message['address'], message

    def send_error(self, address, message):
        """Sends an error to a client.

        :param address: A list containing the identity of the client
            and an empty delimiter.
        :param message: The error message.
        """
        data = {'error': True, 'message': message}
        log.error(message)
        self.send(address, data)

    def send(self, address, message):
        """Sends a message to a client.

        Format of sent message: ['address', '', 'packed_message']

        :param address: A list containing the identity of the client
            and an empty delimiter.
        :param message: The message.
        """
        self.socket.send_multipart(address + [msgpack.packb(message)])

    def destroy(self):
        """Terminate a ZMQ context."""
        self.context.destroy()

    @staticmethod
    def get_key(key, data):
        """Gets an item from a dictionary.

        :param key: The key.
        :param data: A dictionary to search for the key.
        :returns: The value associated with the key, if it exists.
        :raises: MercuryClientException if the key is not present.
        """
        try:
            return data[key]
        except KeyError:
            raise MercuryClientException('{} is missing from request'
                                         .format(key))

    @staticmethod
    def validate_required(required, data):
        """Validates that a message contains the required data.

        :param required: A list of required keys.
        :param data: A dict representing the message.
        :raises: MercuryClientException if the message is missing
            required data.
        """
        missing = []
        for key in required:
            if key not in data:
                missing.append(key)

        if missing:
            raise MercuryClientException('Message is missing required data: {}'
                                         .format(missing))

    def message_handler(self, address, message):
        if isinstance(message, dict) and message.get('_protocol_message') == 'keep_alive':
            log.debug('Keep alive received from {}'.format(address))
            response = {'_protocol_message': 'keep_alive_confirmed'}
        else:
            # noinspection PyBroadException
            try:
                response = self.process(message)
            except MercuryClientException as mce:
                return self.send_error(
                    address,
                    'Encountered client error: {}'.format(
                        mce))
            except Exception:
                exec_dict = parse_exception()
                log.error('process raised an exception and should not have.')
                log.error(fancy_traceback_short(exec_dict))
                return self.send_error(address,
                                       'Encountered server error, sorry')

        self.send(address, response)
        log.debug('Sent {}'.format(address))

    def start(self):
        while not self._kill:
            try:
                if not self.in_poller.poll(self.poll_timeout * 1000):
                    continue
            except KeyboardInterrupt:
                log.info('Interrupted')
                break
            try:
                address, message = self.receive()
            except MercuryClientException:
                continue
            self.message_handler(address, message)
        log.info('Shutting down')

    def process(self, message):
        raise NotImplementedError

    def cleanup(self):
        """Base cleanup() method."""
        self.destroy()
