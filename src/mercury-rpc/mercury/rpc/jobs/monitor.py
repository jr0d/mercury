import asyncio
import datetime
import logging
import time

from mercury.rpc.jobs.tasks import (
    COMPLETED_STATUSES, complete_task
)

log = logging.getLogger(__name__)


class Monitor(object):
    """
    Monitors the tasks collection for expired tasks. Timeout values should accompany tasks. If
    a task does not contain a timeout, default_timeout will be used
    """
    def __init__(self, jobs_collection, tasks_collection, loop, default_timeout=120, cycle_time=10):
        self.jobs_collection = jobs_collection
        self.tasks_collection = tasks_collection
        self.asyncio_loop = loop
        self.default_timeout = default_timeout
        self.cycle_time = cycle_time
        self.last_run = 0

        self._kill = False

    async def process(self):
        log.debug('Processing')
        now = time.time()
        c = self.tasks_collection.find({'status': {'$nin': COMPLETED_STATUSES},
                                        'timeout': {'$gt': 0}})  # A timeout of 0 means no timeout

        log.debug('Matched {} active tasks'.format(await c.count()))
        async for task in c:
            if task['time_updated'] < now - task['timeout']:
                log.error('Timeout Error: Job: {job_id}, Task: {task_id}, Timeout: {timeout}'.format(**task))
                update_data = {
                    'status': 'TIMEOUT',
                    'time_started': task['time_started'] or 0,
                    'time_updated': now,
                    'time_completed': now,
                    'ttl_time_completed': datetime.datetime.utcfromtimestamp(now),
                    'message': None,
                    'traceback': None,
                    'action': 'Task Timeout'
                }
                complete_task(task['job_id'],
                              task['task_id'],
                              update_data,
                              jobs_collection=self.jobs_collection,
                              tasks_collection=self.tasks_collection)

    def kill(self):
        self._kill = True

    async def loop(self):
        while True:
            if self._kill:
                log.info('Kill signal received, shutting down')
                break
            if not self.asyncio_loop.is_running:
                print('loop is not running')
                break
            await self.process()
            await asyncio.sleep(self.cycle_time)

