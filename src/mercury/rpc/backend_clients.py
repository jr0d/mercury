import logging


from mercury.common.asyncio.clients.queue import QueueServiceClient

log = logging.getLogger(__name__)

que_manager_cache = {}
que_client_opts = {
    'linger': 0,
    'response_timeout': -1,
    'rcv_retry': 0,
    'resend_on_timeout': 0
}


def set_queue_client_opts(linger,
                          response_timeout,
                          rcv_retry,
                          resend_on_timeout):
    """
    Sets options that should be used when creating queue clients

    :param linger: The default value of -1 specifies an infinite linger period.
    Pending messages shall not be discarded after a call to zmq_close();
    attempting to terminate the socket's context with zmq_term() shall block
    until all pending messages have been sent to a peer.

    The value of 0 specifies no linger period. Pending messages shall be
    discarded immediately when the socket is closed with zmq_close().

    Positive values specify an upper bound for the linger period in
    milliseconds. Pending messages shall not be discarded after a call to
    zmq_close(); attempting to terminate the socket's context with zmq_term()
    shall block until either all pending messages have been sent to a peer, or
    the linger period expires, after which any pending messages shall be
    discarded.

    :param response_timeout: Timeout waiting on socket to successfully send and
    receive data.
    :param rcv_retry:
    :param resend_on_timeout:
    """
    que_client_opts.update(
        {
            'linger': linger,
            'response_timeout': response_timeout,
            'rcv_retry': rcv_retry,
            'resend_on_timeout': resend_on_timeout
        })


def get_queue_service_client(backend_zurl):
    return QueueServiceClient(backend_zurl, **que_client_opts)
