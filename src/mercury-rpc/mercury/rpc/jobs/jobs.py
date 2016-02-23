import redis
import uuid

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
        pass


if __name__ == '__main__':
    t1 = Task('localhost', 9003, 'echo', ['This is the message'])
    print t1
    print t1.to_dict()
