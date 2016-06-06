class Task(object):
    def __init__(self):
        self.task = None

    def fetch(self):
        raise NotImplementedError

    def _do(self):
        raise NotImplementedError

    def do(self):
        if not self.task:
            raise Exception('Task has not been populated')
        result = self._do()
        self.task = None
        return result

    @classmethod
    def create(cls):
        raise NotImplementedError
