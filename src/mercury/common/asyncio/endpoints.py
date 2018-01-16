"""
async_endpoints is a singleton, allowing dispatch endpoints to be
specified using a decorator. Controllers can define endpoints any way
they see fit. This is here for convenience only.

For an example usage, see mercury.inventory.controller.InventoryController
"""

import inspect
import logging

from mercury.common.exceptions import MercuryClientException

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


class StaticEndpointController(object):
    """Use this if you want to be lazy"""
    def __init__(self):
        self.endpoints = async_endpoints

    # TODO: CODE Duplication, move these static methods to a library module

    @staticmethod
    def get_key(key, d):
        try:
            return d[key]
        except KeyError:
            raise MercuryClientException('{} is missing from request'.format(key))

    @staticmethod
    def validate_required(required, data):
        missing = []
        for key in required:
            if key not in data:
                missing.append(key)

        if missing:
            raise MercuryClientException('Message is missing required data: {}'.format(missing))
