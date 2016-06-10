import logging
import time

log = logging.getLogger(__name__)


class Worker(object):

    def __init__(self, task_handler, maximum_requests, maximum_age):
        self.maximum_requests = maximum_requests
        self.maximum_age = maximum_age
        self.birth = None
        self.kill_signal = None
        self.handled_tasks = 0

        self.task = task_handler.create()

    def start(self):
        self.birth = time.time()
        while self.handled_tasks < self.maximum_requests:
            if self.kill_signal:
                log.info(
                    'Shutting down... I served my masters well: %s tasks ,'
                    'lived %s seconds' % (self.handled_tasks,
                                          time.time() - self.birth))
                break
            task = self.task.fetch()
            if not task:
                continue
            self.task.execute()
            self.handled_tasks += 1
