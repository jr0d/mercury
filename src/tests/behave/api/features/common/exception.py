"""
Commonly used exceptions used in tests.
"""


class BaseBehaveException(Exception):
    message = "Not Set"

    def __init__(self, message=None):
        super(BaseBehaveException, self).__init__()
        self.message = message or self.message

    def __str__(self):
        return repr(self.message)


class TimeoutException(BaseBehaveException):
    message = "Request timed out"
