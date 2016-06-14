import logging
import json
import redis
import time

from mercury.common.task_managers.base.task import Task

log = logging.getLogger(__name__)


class RedisTask(Task):
    def __init__(self, queue_name):
        super(RedisTask, self).__init__()

        self.queue_name = queue_name
        log.debug('Redis QUEUE name: %s' % self.queue_name)

        self.redis = redis.Redis()

    def fetch(self):
        message = self.redis.blpop(self.queue_name, timeout=1)
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
        self.task = task
        return task

    def do(self):
        raise NotImplementedError

    @classmethod
    def create(cls):
        raise NotImplementedError
