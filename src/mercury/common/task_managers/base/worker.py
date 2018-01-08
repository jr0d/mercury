import logging
import time

log = logging.getLogger(__name__)


class Worker(object):
    """Worker executing tasks"""
    def __init__(self, task_handler, maximum_requests, maximum_age,
                 handler_args, handler_kwargs):
        """Create a new Worker to execute tasks.

        :param task_handler: Task handler to fetch and execute tasks.
        :param maximum_requests: Maximum number of tasks this worker can
            execute.
        :param maximum_age: Maximum age of the worker.
        """
        self.maximum_requests = maximum_requests
        self.maximum_age = maximum_age
        self.birth = None
        self.kill_signal = None
        self.handled_tasks = 0

        self.task = task_handler(*handler_args, **handler_kwargs)

    def start(self):
        """Start the worker.

        The worker fetches and executes tasks as long as its maximum number
        of tasks is not reached.
        """
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
