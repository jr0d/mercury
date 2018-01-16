import logging
import queue
import threading

from mercury.common.clients.rpc.queue import QueueServiceClient

log = logging.getLogger(__name__)

que_manager_cache = {}
que_client_opts = {
    'linger': -1,
    'response_timeout': 10
}


def set_queue_client_opts(linger, response_timeout):
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
    """
    que_client_opts.update(
        {
            'linger': linger,
            'response_timeout': response_timeout
        })


def get_queue_manager(zurl):
    """
    Gets a queue manager and caches it.
    :param zurl:
    :return:
    """
    if zurl not in que_manager_cache:
        log.debug(f'Cache miss: Instantiating manager for {zurl}')
        que_manager_cache[zurl] = BackendQueueManager(zurl)
    return que_manager_cache[zurl]


class BackendQueueManager(object):
    """ This class provides a solution for jobs targeting multiple backends.
    When instantiated, the class will create a FIFO queue and spawn a thread
    which will monitor the queue for tasks. Any tasks that it receives will
    be dispatched to the appropriate backend queue backend.
    """

    QUEUE_GET_TIMEOUT = 2

    def __init__(self, backend_zurl):
        """

        :param backend_zurl:
        """
        self.backend_zurl = backend_zurl
        self.client = QueueServiceClient(backend_zurl, **que_client_opts)

        # A queue when can be fed tasks
        self.tasks_queue = queue.Queue()

        # Kill signaler
        self._kill = False

        # Create and start the monitor thread
        self.thread = threading.Thread(target=self.queue_runner)
        self.thread.start()

    def queue_runner(self):
        """ Thread loop responsible for dispatching tasks """
        while not self._kill:
            try:
                task = self.tasks_queue.get(timeout=self.QUEUE_GET_TIMEOUT)
            except queue.Empty:
                continue
            log.debug('Dispatching task to queue service, job_id: {job_id} '
                      'task_id: {task_id} backend: {backend}'.format(**task))

            # Enqueue the task on the backend
            self.client.enqueue_task(task)

    def kill(self):
        log.info('Kill signal receive, shutting down queue manager thread')
        self._kill = True
