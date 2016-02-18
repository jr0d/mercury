import logging
import redis
import time
import uuid

from mercury.common.exceptions import MercuryUserError, MercuryCritical
from mercury.common.mongo import get_collection
from mercury.common.transport import get_ctx_and_connect_req_socket


JOBS_COLLECTION = 'jobs'
log = logging.getLogger(__name__)


class Task(object):
    """
    There is a voice in my head shouting 'JUST SUBCLASS DICT!!!'
    """
    def __init__(self, host, port, method, args=None, kwargs=None):
        self.host = host
        self.port = port
        self.method = method
        self.args = args or []
        self.kwargs = kwargs or {}
        self.task_id = uuid.uuid4()
        self.status = 'NEW'
        self.time_queued, self.time_started, self.time_completed = None

    def to_dict(self):
        return {
            'method': self.method,
            'args': self.args,
            'kwargs': self.kwargs,
            'host': self.host,
            'port': self.port,
            'task_id': str(self.task_id),
            'status': self.status,
            'time_queued': self.time_queued,
            'time_started': self.time_started,
            'time_completed': self.time_completed
        }

    def __repr__(self):
        return 'Task: {task_id} <{host}:{port}> ' \
               '[method: {method} args: {args}, kwargs: {kwargs}]'.format(**self.to_dict())


class Job(object):
    def __init__(self, command, targets, collection):
        """

        :param command: Procedure dictionary containing method, args, kwargs
        :param targets: active inventory targets
        :param collection: mongodb collection object
        :raises MercuryUserError: catch,log, demean, and move on
        :raises MercuryCritical: Halt and catch fire
        """
        self.command = command
        self.targets = targets
        self.collection = collection

        self.method, self.args, self.kwargs = self.__extract_command()
        self.job_id = uuid.uuid4()
        self.tasks = []
        # Populate the tasks

        for target in targets:
            self.tasks.append(self.__create_task(target))

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

        self.__check_method()

        return method, args, kwargs

    def __check_method(self):
        for target in self.targets:
            try:
                capabilities = target['capabilities']
            except KeyError:
                raise MercuryCritical('Encountered malformed target, the database is corrupted')
            if self.method not in capabilities:
                raise MercuryUserError('One of more targets does not support method: %s' % self.method)

    def __create_task(self, target):
        # TODO: select ipv4 or ipv6
        # TODO: add yaml option: prefer_ipv6 (bool)
        try:
            host = target['rpc_address']
            port = target['rpc_port']
        except KeyError:
            raise MercuryCritical('Encountered malformed target, the database is corrupted')

        task = Task(
            host=host,
            port=port,
            method=self.method,
            args=self.args,
            kwargs=self.kwargs
        )

        log.debug('Created task: %s' % task)
        return task

    def to_dict(self):
        return {
            'method': self.method,
            'args': self.args,
            'kwargs': self.kwargs,
            'job_id': str(self.job_id),
            'time_started': self.time_started,
            'time_completed': self.time_completed,
            'tasks': [x.todict() for x in self.tasks]
        }

    def __insert_job(self):
        self.time_started = time.time()
        log.info('Inserting job: %s' % self.job_id)
        self.collection.insert(self.to_dict())


if __name__ == '__main__':
    t1 = Task('localhost', 9003, 'echo', ['This is the message'])
    print t1
    print t1.to_dict()
