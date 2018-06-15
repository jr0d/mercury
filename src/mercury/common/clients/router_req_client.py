import logging

import msgpack
import zmq

from mercury.common.exceptions import (
    parse_exception,
    fancy_traceback_short,
    MercuryTransportError
 )


log = logging.getLogger(__name__)


class RouterReqClient(object):
    service_name = 'Generic Service'

    def __init__(self, zmq_url, linger=-1, response_timeout=-1, rcv_retry=0,
                 raise_on_timeout=False):
        """

        :param zmq_url:
        :param linger:
        :param response_timeout:
        :param rcv_retry: The number of times to retry
        """
        self.zmq_url = zmq_url
        self.linger = linger
        self.response_timeout = response_timeout
        self.rcv_retry = rcv_retry
        self.raise_on_timeout = raise_on_timeout

        self.context = zmq.Context()

        self.socket = None
        log.debug('[{}] Creating connection to {}'.format(self.service_name,
                                                          self.zmq_url))
        self.refresh_socket()

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

            # Keep Alive

            self.socket.setsockopt(zmq.TCP_KEEPALIVE, 1)
            self.socket.setsockopt(zmq.TCP_KEEPALIVE_IDLE, 120)
            self.socket.setsockopt(zmq.TCP_KEEPALIVE_CNT, 3)
            self.socket.setsockopt(zmq.TCP_KEEPALIVE_INTVL, 10)

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

    def safe_receive(self):
        """
        Receive server reply.
        :return: The unpacked message
        """

        # Hacky do while loop. Thanks python...
        retry_count = self.rcv_retry and self.rcv_retry + 1 or 1

        while retry_count:
            # noinspection PyBroadException
            try:
                return msgpack.unpackb(self.socket.recv(), encoding='utf-8')
            except zmq.Again:
                retry_count -= 1
                # TODO: Created message wrapper so we can track these
                log.error(f'[{self.service_name}] Receive timeout'
                          f' Retries remaining: {retry_count}')
            # TODO: explicitly catch things that zmq or msgpack might throw
            # Catchall
            except Exception:
                log.error(f'An unhandled exception occurred while receiving'
                          f' <{fancy_traceback_short(parse_exception())}>')
                break

        # Errors should be actionable
        error_message = f'[{self.service_name}] Failure receiving server ' \
                        f'reply. Closing socket to reset state.'
        log.error(error_message)
        self.close()

        if self.raise_on_timeout:
            raise MercuryTransportError(error_message)

        return {'error': True, 'message': error_message}

    def transceiver(self, payload):
        """
        Convenience method
        :param payload:
        :return:
        """
        self.safe_send(payload)
        return self.safe_receive()

    def close(self):
        """ close the socket """
        self.socket.close()
