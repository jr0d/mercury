import datetime
import logging
import time
import uuid


log = logging.getLogger(__name__)

# TODO: Save space and change these to unsigned shorts?
COMPLETED_STATUSES = ['SUCCESS', 'ERROR', 'EXCEPTION', 'TIMEOUT']


async def update_task(update_data, tasks_collection):
    """
    Helper function that simplifies updating tasks
    :param tasks_collection:
    :param update_data:
    :return:
    """
    # We'll be modifying the update data, so make a copy
    task_update = update_data.copy()

    # Pop and store the task_id
    task_id = task_update.pop('task_id')

    # Remove job_id from update_data, it should already be present
    task_update.pop('job_id', None)

    # update the timestamp
    task_update['time_updated'] = time.time()

    progress = update_data.get('progress')
    # We don't want to overwrite existing progress updates
    if progress:
        task_update['progress'] = progress

    log.info(
        'Task updated: task_id: {}, status: {}, action: {}, progress: {}'.format(
            task_id,
            update_data.get('status', 'UPDATED'),
            update_data.get('action', ''),
            update_data.get('progress', 0),
            update_data.get('traceback')
        ))

    await tasks_collection.update_one(
        filter={'task_id': task_id},
        update={
            '$set': task_update
        }
    )


async def complete_task(response_data, jobs_collection, tasks_collection):
    """
    response_data should include time_started and time_completed from the remote host.
    time_updated and ttl_time_completed are relative to the server.
    :param jobs_collection:
    :param tasks_collection:
    :param task_id:
    :param response_data:
    :return:
    """

    now = time.time()
    ttl_time = datetime.datetime.utcfromtimestamp(now)

    log.info(
        'Task completed: task_id: {task_id} job: {job_id} message: {message}'.format(
            **response_data
        ))

    job_id = response_data.pop('job_id')

    task_update = {
        'task_id': response_data['task_id'],
        'status': response_data['status'],
        'time_completed': now,
        'ttl_time_completed': ttl_time,
        'message': response_data['message'],
        'traceback': response_data.get('traceback'),
        'action': response_data.get('action', '')
    }

    await update_task(task_update, tasks_collection)

    if await is_completed(tasks_collection, job_id):
        log.info('Job completed: {}, status: {}'.format(job_id, response_data[
            'status']))
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
    """

    :param tasks_collection:
    :param job_id:
    :return:
    """
    docs = tasks_collection.find({'job_id': job_id})
    return docs


async def is_completed(tasks_collection, job_id):
    """
    This will likely change once Job statuses are finalized
    :param tasks_collection:
    :param job_id:
    :return:
    """
    return await tasks_collection.count(
        {'job_id': job_id, 'status': {'$nin': COMPLETED_STATUSES}}) == 0


class Task(object):
    """
    status: NEW|DISPATCHED|UPDATED|SUCCESS|ERROR|TIMEOUT|EXCEPTION
    action: Arbitrary and optional action string set by the executor
    progress: Optional progress delta 0 through 1 set by the executor
    ttl_time_completed: an ISO datetime value used by mongo as an expiry index
    """

    def __init__(self, job_id, mercury_id, host, port, method, backend,
                 args=None,
                 kwargs=None):
        """

        :param job_id:
        :param mercury_id:
        :param host:
        :param port:
        :param method:
        :param backend:
        :param args:
        :param kwargs:
        """
        self.job_id = job_id
        self.mercury_id = mercury_id
        self.host = host
        self.port = port
        self.method = method
        self.backend = backend
        self.args = args or []
        self.kwargs = kwargs or {}
        self.message = {}
        self.task_id = uuid.uuid4()
        self.status = 'NEW'
        self.action = 'New Task'
        self.progress = 0
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
            'backend': self.backend,
            'task_id': str(self.task_id),
            'status': self.status,
            'action': self.action,
            'progress': self.progress,
            'time_started': self.time_started,
            'time_completed': self.time_completed,
            'time_updated': self.time_updated,
            'message': self.message,
            'ttl_time_completed': self.ttl_time_completed,
            'timeout': 0
        }

    def __repr__(self):
        return 'Task: {task_id} <{host}:{port}> [{backend}]' \
               '[method: {method} args: {args}, kwargs: {kwargs}]'.format(
            **self.to_dict())

    def enqueue(self, backend):
        """

        :param backend:
        :return:
        """
        log.debug('Queuing task: %s' % self.task_id)
        self.time_updated = time.time()
        backend.enqueue_task(self.to_dict())
