"""
Log handler/dispatcher for
"""


class Handler(object):
    def dispatch(self, message):
        raise NotImplementedError
