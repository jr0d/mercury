import json
import logging
import redis
import time
import uuid

from mercury.common.exceptions import MercuryUserError, MercuryCritical
from mercury.rpc.configuration import TASK_QUEUE, get_jobs_collection
from mercury.rpc.preprocessors import instruction_preprocessors

log = logging.getLogger(__name__)


def update_task_existing_connection(collection, task_id, document):
    """
    Helper function that simplifies updating job tasks by constructing tasks.<task_id>.k
    :param collection:
    :param task_id: The task
    :param document: A dictionary that represents the changes to job task
    :return: return value of pymongo.Collection.insert
    """

    return collection.update_one(
        filter={'task_id': task_id},
        update={
            '$set': document
        }
    )


def update_task(task_id, document):
    """
    Same as above, but creates a new pool. For short running threads
    :param task_id:
    :param document:
    :return:
    """
    collection = get_jobs_collection()
    return update_task_existing_connection(collection, task_id, document)


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
    complete_statuses = ['SUCCESS', 'ERROR', 'EXCEPTION', 'TIMEOUT']  # This will move
    return tasks_collection.count({'job_id': job_id, 'status': {'$nin': complete_statuses}}) == 0


class Task(object):
    """
    There is a voice in my head shouting 'JUST SUBCLASS DICT!!!'
    """
    def __init__(self, job_id, mercury_id, host, port, method, args=None, kwargs=None):
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
        self.time_queued = None
        self.time_started = None
        self.time_completed = None
        self.ttl_time_completed = None

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
            'time_queued': self.time_queued,
            'time_started': self.time_started,
            'time_completed': self.time_completed,
            'result': self.result,
            'ttl_time_completed': self.ttl_time_completed
        }

    def __repr__(self):
        return 'Task: {task_id} <{host}:{port}> ' \
               '[method: {method} args: {args}, kwargs: {kwargs}]'.format(**self.to_dict())

    def enqueue(self):
        log.debug('Queuing task: %s' % self.task_id)
        redis_client = redis.Redis()
        self.time_queued = time.time()
        redis_client.lpush(TASK_QUEUE, json.dumps(self.to_dict()))


class Job(object):
    def __init__(self, instruction, targets, jobs_collection, tasks_collection):
        """
        :param instruction: Procedure dictionary containing method, args, kwargs
        :param targets: active inventory targets
        :param collection: mongodb collection object (capped)
        :raises MercuryUserError: catch, log, demean, and move on
        :raises MercuryCritical: Halt and catch fire
        """
        self.instruction = instruction
        self.targets = targets
        self.jobs_collection = jobs_collection
        self.tasks_collection = tasks_collection

        self.preprocessor = None
        self.primitive = False

        self.job_id = uuid.uuid4()
        self.tasks = {}
        # Populate the tasks

        for target in targets:
            task = self.__create_task(target)
            self.tasks[str(task.task_id)] = task

        self.task_count = len(targets)

        self.time_started = None
        self.time_completed = None
        self.ttl_time_completed = None

    def __check_method(self, method):
        for target in self.targets:
            try:
                capabilities = target['capabilities']
            except KeyError:
                raise MercuryCritical('Encountered malformed target, the database is corrupted')
            if method not in capabilities:
                raise MercuryUserError('One of more targets does not support method: %s' % method)

    def __create_task(self, target):
        # TODO: select ipv4 or ipv6
        # TODO: add yaml option: prefer_ipv6 (bool)
        try:
            mercury_id = target['mercury_id']
            host = target['rpc_address']
            port = target['rpc_port']
        except KeyError:
            raise MercuryCritical('Encountered malformed target, the database is corrupted')

        # Preprocessor entry

        method = self.instruction.get('method')
        if method:
            self.primitive = True
            call_data = {
                'method': self.instruction['method'],
                'args': self.instruction.get('args', []),
                'kwargs': self.instruction.get('kwargs', {})
            }

        else:
            self.preprocessor = self.instruction.get('preprocessor')
            if not self.preprocessor:
                raise MercuryUserError('Contract invalid')

            preprocessor = instruction_preprocessors.get(self.preprocessor)
            if not preprocessor:
                raise MercuryUserError('Specified preprocessor does not exist')

            log.info('Calling %s preprocessor' % preprocessor['name'])
            call_data = preprocessor['entry'](target, self.instruction)

        task = Task(
            job_id=self.job_id,
            mercury_id=mercury_id,
            host=host,
            port=port,
            **call_data
        )

        log.debug('Created task: %s' % task)
        return task

    def to_dict(self):
        return {
            'job_id': str(self.job_id),
            'time_started': self.time_started,
            'time_completed': self.time_completed,
            'ttl_time_completed': self.ttl_time_completed,
            'instruction': self.instruction,
            'task_count': self.task_count
        }

    def __insert_job(self):
        self.time_started = time.time()

        for task in list(self.tasks.values()):
            task.enqueue()

        log.info('Inserting job: %s' % self.job_id)

        self.jobs_collection.insert_one(self.to_dict())
        self.tasks_collection.insert_many([task.to_dict() for task in list(self.tasks.values())])

    def start(self):
        self.__insert_job()
