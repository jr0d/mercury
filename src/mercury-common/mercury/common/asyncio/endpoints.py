import inspect
import logging


log = logging.getLogger(__name__)


async_endpoints = dict()


def async_endpoint(name):
    def add(f):
        log.debug('Adding async runtime endpoint {} ({})'.format(f.__name__, name))
        if not inspect.iscoroutinefunction(f):
            log.error('{} is not a coroutine'.format(f.__name__))
        elif name in async_endpoints:
            log.error('{} already exists in table'.format(name))
        else:
            async_endpoints[name] = f
        return f
    return add
