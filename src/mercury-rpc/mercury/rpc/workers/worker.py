import json
import logging
import redis
import signal
import threading
import time

from mercury.common.transport import SimpleRouterReqClient
from mercury.rpc.jobs import update_job_task

log = logging.getLogger(__name__)


class Worker(object):
    def __init__(self, task_queue_name, maximum_requests, maximum_age):
        self.task_queue_name = task_queue_name
        self.maximum_requests = maximum_requests
        self.maximum_age = maximum_age
        self.birth = None
        self.redis = redis.Redis()
        self.kill_signal = None
        self.handled_tasks = 0

    def fetch_task(self):
        message = self.redis.blpop(self.task_queue_name, timeout=1)
        if not message:
            return
        message = message[1]
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
        log.debug('Dispatching task: %s' % task)
        response = client.transceiver(_payload)
        if response['status'] != 0:
            update_job_task(task['job_id'], task['task_id'], {'status': 'ERROR',
                                                              'response': 'Dispatch Error: %s' % response})
        return response

    def start(self):
        self.birth = time.time()
        while self.handled_tasks < self.maximum_requests:
            if self.kill_signal:
                log.info(
                    'Shutting down... I served my masters well: %s tasks ,'
                    'lived %s seconds' % (self.handled_tasks,
                                          time.time() - self.birth))
                break
            task = self.fetch_task()
            if not task:
                continue
            response = self.dispatch_task(task)
            log.debug('Task dispatched: %s' % response)
            self.handled_tasks += 1


class Manager(object):
    def __init__(self, task_queue_name, number_of_workers=10, maximum_requests_per_thread=5000, maximum_age=3600):
        self.task_queue_name = task_queue_name
        self.number_of_workers = number_of_workers
        self.max_requests = maximum_requests_per_thread
        self.max_age = maximum_age

        self.workers = []

    def spawn(self):
        worker_dict = {}
        w = Worker(self.task_queue_name, self.max_requests, self.max_age)
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

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    manager = Manager('rpc_tasks', 10, 3600)
    manager.manage()

