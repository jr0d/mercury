import logging

import msgpack
import zmq
import zmq.asyncio

from mercury.common.exceptions import (
    parse_exception,
    fancy_traceback_short,
    MercuryTransportError
)

log = logging.getLogger(__name__)


class AsyncRouterReqClient(object):
    service_name = 'Generic Service'

    def __init__(self, zmq_url, linger=-1, response_timeout=-1, rcv_retry=0,
                 raise_on_timeout=False, resend_on_timeout=0):
        """

        :param zmq_url:
        :param linger:
        :param response_timeout:
        :param rcv_retry: The number of times to retry
        :param raise_on_timeout: Raise an exception on timeout
        :param resend_on_timeout: Attempt to re-transmit messages on timeout x
        number of times
        """
        self.zmq_url = zmq_url
        self.linger = linger
        self.response_timeout = response_timeout
        self.raise_on_timeout = raise_on_timeout

        self.context = zmq.asyncio.Context()

        # Ensure that we try at least once
        self.rcv_retry = rcv_retry and rcv_retry + 1 or 1
        self.resend_on_timeout = resend_on_timeout \
            and resend_on_timeout + 1 or 1

        self.socket = None
        self.refresh_socket()

        log.debug('Client Initialized: {} , linger: {}, response_timeout: {},'
                  ' rcv_retry: {}, resend_on_timeout'.format(
                                                        self.service_name,
                                                        self.linger,
                                                        self.response_timeout,
                                                        rcv_retry,
                                                        resend_on_timeout))

    def refresh_socket(self):
        """
        Creates a new socket if socket is None or the socket is closed
        :return:
        """
        if not self.socket or self.socket.closed:
            self.socket = self.context.socket(zmq.REQ)

            # < -1 is not supported, so assume anything less than 0 should be
            # -1
            if self.response_timeout < 0:
                timeout = -1
            else:
                # positive timeouts should be expressed in milliseconds
                timeout = self.response_timeout * 1000

            self.socket.setsockopt(zmq.LINGER, self.linger)
            self.socket.setsockopt(zmq.RCVTIMEO, timeout)
            self.socket.connect(self.zmq_url)

    def safe_send(self, data):
        """
        Ensures that the socket is alive by calling refresh_socket
        :return:
        """
        # Refresh the socket if necessary
        self.refresh_socket()

        # Pack data
        packed = msgpack.packb(data)

        # Send does not block
        self.socket.send_multipart([packed])

    async def safe_receive(self):
        """
        Receive server reply.
        :return: The unpacked message
        """
        retry_count = self.rcv_retry

        while retry_count:
            # noinspection PyBroadException
            try:
                return msgpack.unpackb(
                    await self.socket.recv(), encoding='utf-8')
            except zmq.Again:
                retry_count -= 1
                log.error(f'[{self.service_name}] Receive timeout from '
                          f'{self.zmq_url} . Retries remaining: {retry_count}')
            # TODO: explicitly catch things that zmq or msgpack might throw
            # Catchall
            except Exception:
                log.error(f'An unhandled exception occurred while receiving'
                          f' from {self.zmq_url} '
                          f'<{fancy_traceback_short(parse_exception())}>')
                break

        # Errors should be actionable
        error_message = f'[{self.service_name}] Failure receiving server ' \
                        f'reply from {self.zmq_url}. Closing socket to reset ' \
                        f'state.'
        log.error(error_message)
        self.close()

        if self.raise_on_timeout:
            raise MercuryTransportError(error_message)

        return {'error': True, 'message': error_message, 'timeout': True}

    async def transceiver(self, payload):
        """
        :param payload:
        :return:
        """

        attempts = self.resend_on_timeout
        result = {}

        while attempts:
            self.safe_send(payload)
            result = await self.safe_receive()
            if not result.get('timeout'):
                break

            log.error('[{}] Failed to transmit data to {}. Attempting to '
                      'resend {} more time(s)'.format(self.service_name,
                                                      self.zmq_url,
                                                      attempts))
            attempts -= 1

        return result

    def close(self):
        """ close the socket """
        self.socket.close()
