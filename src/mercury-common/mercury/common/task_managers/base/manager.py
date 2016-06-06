import logging
import signal
import threading
import time

from .worker import Worker


log = logging.getLogger(__name__)


class Manager(object):
    def __init__(self, task_handler, number_of_workers=10, maximum_requests_per_thread=5000, maximum_age=3600):
        self.number_of_workers = number_of_workers
        self.max_requests = maximum_requests_per_thread
        self.max_age = maximum_age
        self.task_handler = task_handler
        self.workers = []

    def spawn(self):
        worker_dict = {}
        w = Worker(self.task_handler, self.max_requests, self.max_age)
        worker_dict['worker_class'] = w
        t = threading.Thread(target=w.start)
        t.start()
        log.info('Spawned thread: %s' % t.ident)
        worker_dict['thread'] = t
        self.workers.append(worker_dict)

    def kill_all(self):
        for worker in self.active_workers:
            log.info('Sending kill signal to worker %s' % worker['thread'].ident)
            worker['worker_class'].kill_signal = True

    @property
    def active_workers(self):
        active = []
        for idx in range(len(self.workers)):
            if self.workers[idx]['thread'].is_alive():
                active.append(self.workers[idx])
            else:
                # An optimization that usually should be present in a property
                # "I'm sure you can find a better way to implement this" - Hussam
                self.workers.pop(idx)
        return active

    def spawn_threads(self):
        count = len(self.active_workers)
        while count <= self.number_of_workers:
            self.spawn()
            count += 1

    def manage(self):
        # noinspection PyUnusedLocal
        def term_handler(*args, **kwargs):
            log.info('Caught TERM signal, sending kill all')
            self.kill_all()

        signal.signal(signal.SIGTERM, term_handler)

        try:
            while True:
                self.spawn_threads()
                time.sleep(.01)
        except KeyboardInterrupt:
            term_handler()