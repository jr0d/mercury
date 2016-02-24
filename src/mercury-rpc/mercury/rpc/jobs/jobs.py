import redis
import uuid

from mercury.common.exceptions import MercuryUserError
from mercury.common.mongo import get_collection
from mercury.common.transport import get_ctx_and_connect_req_socket

JOBS_COLLECTION = 'jobs'


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

    def to_dict(self):
        return {
            'method': self.method,
            'args': self.args,
            'kwargs': self.kwargs,
            'host': self.host,
            'port': self.port,
            'task_id': str(self.task_id),
            'status': self.status
        }

    def __repr__(self):
        return 'Task: {task_id} <{host}:{port}> ' \
               '[method: {method} args: {args}, kwargs: {kwargs}]'.format(**self.to_dict())


class Job(object):
    def __init__(self, command, targets):
        """

        :param command: Procedure dictionary containing method, args, kwargs
        :param targets: active inventory targets
        :raises: MercuryUserError
        """
        self.command = command
        self.targets = targets

        self.method, self.args, self.kwargs = self.__extract_command()

        self.tasks = []
        # Populate the tasks

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

        self.__validate_method()

        return method, args, kwargs

    def __validate_method(self):
        for target in self.targets:
            try:
                capabilities = target['capabilities']
            except KeyError:
                raise MercuryUserError('One of more targets is malformed, missing capabilities structure')
            if self.method not in capabilities:
                raise MercuryUserError('One of more targets does not support method: %s' % self.method)

if __name__ == '__main__':
    t1 = Task('localhost', 9003, 'echo', ['This is the message'])
    print t1
    print t1.to_dict()
