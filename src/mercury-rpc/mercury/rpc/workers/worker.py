import logging
import signal
import threading


log = logging.getLogger(__name__)


class Worker(object):
    pass


class Manager(object):
    def __init__(self, task_queue, workers=10):


