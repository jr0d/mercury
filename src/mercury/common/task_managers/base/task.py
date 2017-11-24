import logging

log = logging.getLogger(__name__)


class Task(object):
    def __init__(self):
        self.task = None

    def fetch(self):
        raise NotImplementedError

    def do(self):
        raise NotImplementedError

    def execute(self):
        if not self.task:
            raise Exception('Task has not been populated')
        result = self.do()
        self.task = None
        return result
