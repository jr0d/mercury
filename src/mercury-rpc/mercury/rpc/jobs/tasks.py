import datetime
import json
import logging
import redis
import time
import uuid

from mercury.rpc.mongo import get_rpc_collections


log = logging.getLogger(__name__)

# TODO: Save space and change these to unsigned shorts?
COMPLETED_STATUSES = ['SUCCESS', 'ERROR', 'EXCEPTION', 'TIMEOUT']
# This will move


async def update_task(task_id, update_data, tasks_collection=None):
    """
    Helper function that simplifies updating job tasks
    :param tasks_collection:
    :param task_id:
    :param update_data:
    :return:
    """
    collection = tasks_collection or get_rpc_collections().tasks_collection

    # We'll be modifying the update data, so make a copy
    task_update = update_data.copy()

    # Make sure task_id and job_id are not present
    task_update.pop('task_id', None)
    task_update.pop('job_id', None)

    # update the timestamp
    task_update['time_updated'] = time.time()

    progress = update_data.get('progress')
    # We don't want to overwrite existing progress updates
    if progress:
        task_update['progress'] = progress

    log.info('Task updated: task_id: {}, status: {}, action: {}, progress: {}'.format(
        task_id,
        update_data.get('status', 'UPDATED'),
        update_data.get('action', ''),
        update_data.get('progress', 0)
    ))

    await collection.update_one(
        filter={'task_id': task_id},
        update={
            '$set': task_update
        }
    )


async def complete_task(job_id, task_id, response_data, jobs_collection=None, tasks_collection=None):
    """
    response_data should include time_started and time_completed from the remote host.
    time_updated and ttl_time_completed are relative to the server.
    :param job_id:
    :param jobs_collection:
    :param tasks_collection:
    :param task_id:
    :param response_data:
    :return:
    """
    jobs_collection = jobs_collection or get_jobs_collection()
    tasks_collection = tasks_collection or get_tasks_collection()

    now = time.time()
    ttl_time = datetime.datetime.utcfromtimestamp(now)

    task_update = {
        'status': response_data['status'],
        'time_started': response_data['time_started'],
        'time_updated': now,
        'time_completed': response_data['time_completed'],
        'ttl_time_completed': ttl_time,
        'message':  response_data['message'],
        'traceback': response_data['traceback_info'],
        'action': response_data.get('action', '')
    }

    await update_task(task_id, task_update, tasks_collection)

    log.info('Task completed: task_id: {task_id} job: {job_id} message: {message}'.format(
            **response_data
        ))

    if await is_completed(tasks_collection, job_id):
        log.info('Job completed: {}, status: {}'.format(job_id, response_data['status']))
        await jobs_collection.update_one(
            {
                'job_id': job_id
            },
            {
                '$set': {
                    'time_completed': now,
                    'ttl_time_completed': ttl_time
                }
            }
        )


async def get_tasks(tasks_collection, job_id):
    docs = tasks_collection.find({'job_id': job_id})
    return docs


async def is_completed(tasks_collection, job_id):
    """
    This will likely change once Job statuses are finalized
    :param tasks_collection:
    :param job_id:
    :return:
    """
    return await tasks_collection.count({'job_id': job_id, 'status': {'$nin': COMPLETED_STATUSES}}) == 0


class Task(object):
    """
    status: NEW|DISPATCHED|UPDATED|SUCCESS|ERROR|TIMEOUT|EXCEPTION
    action: Arbitrary and optional action string set by the executor
    progress: Optional progress delta 0 through 1 set by the executor
    ttl_time_completed: an ISO datetime value used by mongo as an expiry index
    """
    def __init__(self, job_id, mercury_id, host, port, method, args=None,
                 kwargs=None):
        """

        :param job_id:
        :param mercury_id:
        :param host:
        :param port:
        :param method:
        :param args:
        :param kwargs:
        """
        self.job_id = job_id
        self.mercury_id = mercury_id
        self.host = host
        self.port = port
        self.method = method
        self.args = args or []
        self.kwargs = kwargs or {}
        self.message = {}
        self.task_id = uuid.uuid4()
        self.status = 'NEW'
        self.action = 'New Task'
        self.progress = 0
        self.time_queued = None
        self.time_started = None
        self.time_completed = None
        self.time_updated = None
        self.ttl_time_completed = None
        self.timeout = 0

    def to_dict(self):
        return {
            'method': self.method,
            'args': self.args,
            'kwargs': self.kwargs,
            'mercury_id': self.mercury_id,
            'job_id': str(self.job_id),
            'host': self.host,
            'port': self.port,
            'task_id': str(self.task_id),
            'status': self.status,
            'action': self.action,
            'progress': self.progress,
            'time_queued': self.time_queued,
            'time_started': self.time_started,
            'time_completed': self.time_completed,
            'time_updated': self.time_updated,
            'message': self.message,
            'ttl_time_completed': self.ttl_time_completed,
            'timeout': 0
        }

    def __repr__(self):
        return 'Task: {task_id} <{host}:{port}> ' \
               '[method: {method} args: {args}, kwargs: {kwargs}]'.format(**self.to_dict())

    def enqueue(self, task_queue):
        log.debug('Queuing task: %s' % self.task_id)
        redis_client = redis.Redis()
        self.time_queued = time.time()
        self.time_updated = time.time()
        redis_client.lpush(task_queue, json.dumps(self.to_dict()))
