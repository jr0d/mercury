import json
import logging
import redis
import signal
import threading
import time

from mercury.common.transport import SimpleRouterReqClient

log = logging.getLogger(__name__)


class Worker(object):
    def __init__(self, task_queue_name, maximum_requests, maximum_age):
        self.task_queue_name = task_queue_name
        self.maximum_requests = maximum_requests
        self.maximum_age = maximum_age
        self.birth = None
        self.redis = redis.Redis()

    def fetch_task(self):
        message = self.redis.blpop(self.task_queue_name)[1]
        try:
            task = json.loads(message)
        except ValueError:
            log.error('Popped some bad data off the queue')
            log.debug('DATA: %s' % message)
            return

        log.debug('Fetched task %s; it was %s seconds old' % (
            task['task_id'],
            time.time() - task['time_queued']
        ))
        return task

    @staticmethod
    def update_job(task):
        pass

    @staticmethod
    def dispatch_task(task):
        url = 'tcp://{host}:{port}'.format(**task)
        client = SimpleRouterReqClient(url)
        _payload = {
            'category': 'rpc',
            'method': task['method'],
            'args': task['args'],
            'kwargs': task['kwargs'],
            'task_id': task['task_id'],
            'job_id': task['job_id']
        }
        response = client.transceiver(_payload)
        return response

    def start(self):
        self.birth = time.time()

        while self.maximum_requests:
            task = self.fetch_task()
            response = self.dispatch_task(task)
            print response
            self.maximum_requests -= 1


class Manager(object):
    def __init__(self, task_queue_name, number_of_workers=10, maximum_requests_per_thread=5000):
        self.task_queue_name = task_queue_name
        self.number_of_workers = number_of_workers
        self.max_requests = maximum_requests_per_thread

        self.workers = []


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    w = Worker('rpc_tasks', 10, 3600)
    _task = w.fetch_task()
    print _task
    print w.dispatch_task(_task)
