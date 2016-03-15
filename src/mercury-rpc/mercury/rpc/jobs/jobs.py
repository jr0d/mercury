import json
import logging
import redis
import time
import uuid

from mercury.common.exceptions import MercuryUserError, MercuryCritical
from mercury.common.mongo import get_collection
from mercury.rpc.configuration import db_configuration, TASK_QUEUE


log = logging.getLogger(__name__)


def get_jobs_collection(db='', collection='', servers=None, replica_set=None):
    jobs_db = db or db_configuration.get('jobs_mongo_db', 'test')
    jobs_collection = collection or db_configuration.get('jobs_mongo_collection', 'rpc_jobs')
    jobs_servers = servers or db_configuration.get('jobs_mongo_servers', 'localhost')
    replica_set = replica_set or db_configuration.get('jobs_replica_set')

    return get_collection(
        jobs_db,
        jobs_collection,
        server_or_servers=jobs_servers,
        replica_set=replica_set
    )


def update_job_task_existing_connection(collection, job_id, task_id, document):
    """
    Helper function that simplifies updating job tasks by constructing tasks.<task_id>.k
    :param job_id: The job
    :param task_id: The task
    :param document: A dictionary that represents the changes to job task
    :return: return value of pymongo.Collection.update
    """
    selector = 'tasks.{task_id}'.format(task_id=task_id)
    updated_dict = {}
    for k, v in document.items():
        accessor = '%s.%s' % (selector, k)
        # log.debug('Updating: %s => %s' % (accessor, v))
        updated_dict['%s.%s' % (selector, k)] = v

    return collection.update(
        spec={'job_id': job_id},
        document={
            '$set': updated_dict
        }
    )


def update_job_task(job_id, task_id, document):
    """
    Same as above, but creates a new pool. For short running threads
    :param job_id:
    :param task_id:
    :param document:
    :return:
    """
    collection = get_jobs_collection()
    return update_job_task_existing_connection(collection, job_id, task_id, document)


def get_tasks(collection, job_id):
    doc = collection.find_one({'job_id': job_id}, projection={'tasks': 1, '_id': 0})
    return doc.get('tasks') or {}


def is_completed(collection, job_id):
    """
    This will likely change once Job statuses are finalized
    :param collection:
    :param job_id:
    :return:
    """
    complete_statuses = ['SUCCESS', 'ERROR', 'EXCEPTION', 'TIMEOUT'] # This will move
    tasks = get_tasks(collection, job_id)
    for task_id in tasks:
        if tasks[task_id]['status'] not in complete_statuses:
            return False
    return True


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
        self.time_queued, self.time_started, self.time_completed = [None, None, None]

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
            'result': self.result
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
    def __init__(self, command, targets, collection):
        """

        :param command: Procedure dictionary containing method, args, kwargs
        :param targets: active inventory targets
        :param collection: mongodb collection object (capped)
        :raises MercuryUserError: catch, log, demean, and move on
        :raises MercuryCritical: Halt and catch fire
        """
        self.command = command
        self.targets = targets
        self.collection = collection

        self.method, self.args, self.kwargs = self.__extract_command()
        self.job_id = uuid.uuid4()
        self.tasks = {}
        # Populate the tasks

        for target in targets:
            task = self.__create_task(target)
            self.tasks[str(task.task_id)] = task

        self.time_started = None
        self.time_completed = None

    def __extract_command(self):
        """
        command should be a dictionary containing the full procedure call
        :return: Extracted method(str), args(list), and kwargs(dict)
        """
        try:
            method = self.command['method']
        except KeyError:
            raise MercuryUserError('Job is missing method key')

        args = self.command.get('args') or []
        kwargs = self.command.get('kwargs') or {}

        self.__check_method(method)

        return method, args, kwargs

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

        task = Task(
            job_id=self.job_id,
            mercury_id=mercury_id,
            host=host,
            port=port,
            method=self.method,
            args=self.args,
            kwargs=self.kwargs
        )

        log.debug('Created task: %s' % task)
        return task

    def to_dict(self):
        tasks_dict = dict()
        for task in self.tasks.values():
            tasks_dict[str(task.task_id)] = task.to_dict()

        return {
            'method': self.method,
            'args': self.args,
            'kwargs': self.kwargs,
            'job_id': str(self.job_id),
            'time_started': self.time_started,
            'time_completed': self.time_completed,
            'tasks': tasks_dict
        }

    def __insert_job(self):
        self.time_started = time.time()

        for task in self.tasks.values():
            task.enqueue()

        log.info('Inserting job: %s' % self.job_id)

        self.collection.insert_one(self.to_dict())

    def start(self):
        self.__insert_job()
