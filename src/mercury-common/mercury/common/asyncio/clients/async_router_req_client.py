import logging

import msgpack
import zmq
import zmq.asyncio

from mercury.common.exceptions import MercuryClientException


log = logging.getLogger(__name__)


def get_ctx_and_connect_req_socket(zmq_url):
    """Creates a ZMQ context and a REQ socket.

    :param zmq_url: URL for the socket to connect to.
    :returns: A tuple containing the ZMQ context and the socket.
    """
    ctx = zmq.asyncio.Context()
    # noinspection PyUnresolvedReferences
    socket = ctx.socket(zmq.REQ)
    log.debug('Connection to: {}'.format(zmq_url))
    socket.connect(zmq_url)

    return ctx, socket


class AsyncRouterReqClient(object):
    _service_name = 'Generic router'

    def __init__(self, zmq_url, linger=-1, response_timeout=0):
        self.zmq_url = zmq_url
        self.ctx, self.socket = get_ctx_and_connect_req_socket(self.zmq_url)

        self.socket.setsockopt(zmq.LINGER, linger)
        self.poller = zmq.asyncio.Poller()
        self.poller.register(self.socket, flags=zmq.POLLIN)
        self.response_timeout = response_timeout

    def raise_reply_error(self, reply):
        """Raise a MercuryCritical exception.

        Called when the client cannot talk to the inventory service.
        :raises: MercuryClientException.
        """
        raise MercuryClientException(
            'Problem talking to {} service: message = {}, tb = {}'.format(
                self._service_name,
                reply.get('message'),
                '\n'.join(reply.get('tb', []))
            ))

    def check_and_return(self, reply):
        """Check a transceiver's reply for errors.

        :param reply: A dictionary containing the transceiver's reply.
        :returns: The 'response' field of the transceiver's reply.
        """
        if reply.get('error'):
            self.raise_reply_error(reply)
            print(reply)
        return reply.get('message') or reply.get('response')

    async def transceiver(self, payload):
        """Sends and receives messages.

        :param payload: A dict representing the message to send.
        :returns: A string representing the unpacked response.
        """

        packed = msgpack.packb(payload)

        await self.socket.send_multipart([packed])

        if self.response_timeout:
            if not await self.poller.poll(self.response_timeout * 1000):
                raise IOError('Timeout while waiting for server response')

        rep = await self.socket.recv()

        return self.check_and_return(msgpack.unpackb(rep, encoding='utf-8'))

    def close(self):
        self.socket.close()

