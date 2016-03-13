import json
import logging
import redis
import signal
import threading
import time

log = logging.getLogger(__name__)


class Worker(object):
    def __init__(self, task_queue_name, maximum_requests, maximum_age):
        self.task_queue_name = task_queue_name
        self.maximum_requests = maximum_requests
        self.maximum_age = maximum_age
        self.birth = None
        self.redis = redis.Redis()

    def fetch_work(self):
        message = self.redis.blpop(self.task_queue_name)[1]
        try:
            work = json.loads(message)
        except ValueError:
            log.error('Popped some bad data off the queue')
            log.debug('DATA: %s' % message)
            return

        log.debug('Fetched task %s for work it was %s seconds old' % (
            work['task_id'],
            time.time() - work['time_queued']
        ))
        return work

    def start(self):
        self.birth = time.time()

        while self.maximum_requests:
            work = self.fetch_work()


class Manager(object):
    def __init__(self, task_queue_name, number_of_workers=10, maximum_requests_per_thread=5000):
        self.task_queue_name = task_queue_name
        self.number_of_workers = number_of_workers
        self.max_requests = maximum_requests_per_thread

        self.workers = []


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    w = Worker('rpc_tasks', 10, 3600)
    print w.fetch_work()
