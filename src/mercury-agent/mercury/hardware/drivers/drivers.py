import logging

log = logging.getLogger(__name__)
registered_drivers = list()


class DriverBase(object):
    _handler = None

    def __init__(self, device_info):
        self.device_info = device_info

    def probe(self):
        raise NotImplementedError

    @property
    def handler(self):
        raise NotImplementedError


def driver():
    def decorator(cls):
        log.info('Registering driver: %s' % cls.__name__)
        registered_drivers.append(cls)
        return cls
    return decorator
