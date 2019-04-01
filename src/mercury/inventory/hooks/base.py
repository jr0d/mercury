import logging

log = logging.getLogger(__name__)


class HookException(Exception):
    pass


class Hook(object):
    """
    Base Hook class. Hooks provide a way to manage inventory data before or
    after it is inserted or updated in the database and run additional
    processes if needed.
    """

    def __init__(self, data, *args, **kwargs):
        self.data = data

    def run(self):
        pass
