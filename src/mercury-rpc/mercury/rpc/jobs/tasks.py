import datetime
import json
import logging
import redis
import time
import uuid

from mercury.rpc.configuration import TASK_QUEUE, get_jobs_collection


log = logging.getLogger(__name__)

# TODO: Save space and change these to unsigned shorts?
COMPLETED_STATUSES = ['SUCCESS', 'ERROR', 'EXCEPTION', 'TIMEOUT']  # This will move


def update_task_existing_connection(collection, task_id, update_data):
    """
    Helper function that simplifies updating job tasks by constructing tasks.<task_id>.k
    :param collection:
    :param task_id: The task
    :param update_data: A dictionary that represents the changes to job task
    :return: return value of pymongo.Collection.insert
    """

    task_update = {
        'status': 'UPDATED',
        'action': update_data['action'],
        'time_updated': time.time()
    }

    log.info('Task updated: task_id: {task_id} action: {action}'.format(
        **update_data
    ))

    return collection.update_one(
        filter={'task_id': task_id},
        update={
            '$set': task_update
        }
    )


def update_task(task_id, update_data):
    """
    Same as above, but creates a new pool. For short running threads
    :param task_id:
    :param update_data:
    :return:
    """
    collection = get_jobs_collection()

    return update_task_existing_connection(collection, task_id, update_data)


def complete_task(jobs_collection, tasks_collection, job_id, task_id, response_data):
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
        'action': response_data['action']
    }

    log.info('Task completed: task_id: {task_id} job: {job_id} result: {result}'.format(
            **response_data
        ))

    update_task_existing_connection(tasks_collection, task_id, task_update)

    if is_completed(tasks_collection, job_id):
        log.info('Job completed: {}, status: {}'.format(job_id, response_data['status']))
        jobs_collection.update_one(
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


def get_tasks(tasks_collection, job_id):
    docs = tasks_collection.find({'job_id': job_id})
    return docs or []


def is_completed(tasks_collection, job_id):
    """
    This will likely change once Job statuses are finalized
    :param tasks_collection:
    :param job_id:
    :return:
    """
    return tasks_collection.count({'job_id': job_id, 'status': {'$nin': COMPLETED_STATUSES}}) == 0


class Task(object):
    """
    There is a voice in my head shouting 'JUST SUBCLASS DICT!!!'

    status: NEW|DISPATCHED|UPDATED|SUCCESS|ERROR|TIMEOUT|EXCEPTION
    action: Arbitrary and optional action string set by the executor
    progress: Optional progress delta 0 through 1 set by the executor
    ttl_time_completed: an ISO datetime value used by mongo as an expiry index
    """
    def __init__(self, job_id, mercury_id, host, port, method, args=None, kwargs=None):
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
        self.result = {}
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
            'result': self.result,
            'ttl_time_completed': self.ttl_time_completed,
            'timeout': 0
        }

    def __repr__(self):
        return 'Task: {task_id} <{host}:{port}> ' \
               '[method: {method} args: {args}, kwargs: {kwargs}]'.format(**self.to_dict())

    def enqueue(self):
        log.debug('Queuing task: %s' % self.task_id)
        redis_client = redis.Redis()
        self.time_queued = time.time()
        self.time_updated = time.time()
        redis_client.lpush(TASK_QUEUE, json.dumps(self.to_dict()))
