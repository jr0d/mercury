# Copyright 2015 Jared Rodriguez (jared at blacknode dot net)
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import logging
from pymongo import MongoClient

from mercury.inventory.exceptions import EndpointError

LOG = logging.getLogger(__name__)

runtime_endpoints = {}

__all__ = ['InventoryController']


def endpoint(name):
    def wrap(f):
        def wrapped_f(self, *args, **kwargs):
            return f(self, *args, **kwargs)

        LOG.debug('Adding runtime endpoint %s (%s)' % (f.__name__, name))
        runtime_endpoints[name] = f
        wrapped_f.__name__ = f.__name__
        wrapped_f.__doc__ = f.__doc__
        return wrapped_f
    return wrap


class InventoryController(object):
    def __init__(self):
        self.endpoints = runtime_endpoints

    @endpoint('index')
    def index(self):
        return 'Hello World'

    @endpoint('add')
    def add(self, **kwargs):
        mercury_id = kwargs.get('mercury_id')


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    ic = InventoryController()
    print ic.endpoints
    print ic.index()
    print ic.endpoints['index'](ic)
