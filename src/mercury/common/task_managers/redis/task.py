import logging
import json
import redis

from mercury.common.task_managers.base.task import Task

log = logging.getLogger(__name__)


class RedisTask(Task):
    def __init__(self, redis_host, redis_port, queue_name):
        """Create a new RedisTask task handler.

        :param queue_name: Name of the queue to fetch the tasks from.
        """
        super(RedisTask, self).__init__()

        self.queue_name = queue_name
        log.debug('Redis QUEUE name: %s' % self.queue_name)

        self.redis = redis.Redis(redis_host, redis_port)

    def fetch(self):
        """Fetch a task from the queue.

        The format of the message retrieved from the queue is:
            [queue_name, task_json]

        :returns: dict or None. A dictionary representing the task,
            or None if no task was found or its format is incorrect.
        """
        message = self.redis.blpop(self.queue_name, timeout=1)
        if not message:
            return
        message = message[1]
        if isinstance(message, bytes):
            message = message.decode()
        try:
            task = json.loads(message)
        except ValueError:
            log.error('Popped some bad data off the queue')
            log.debug('DATA: %s' % message)
            return

        log.debug(f'Fetched task {task["task_id"]}')
        self.task = task
        return task

    def do(self):
        raise NotImplementedError

