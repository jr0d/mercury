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

LOG = logging.getLogger(__name__)

runtime_capabilities = {}


def add_capability(entry, name, description, doc=None, serial=False, num_args=None, kwarg_names=None):
    LOG.info('Adding capability %s' % name)
    runtime_capabilities[name] = {
        'name': name,
        'entry': entry,
        'description': description,
        'doc': doc,
        'serial': serial,
        'num_args': num_args,
        'kwarg_names': kwarg_names
    }


def capability(name, description, serial=False, num_args=None, kwarg_names=None):
    def wrap(entry):
        add_capability(entry, name, description, doc=entry.__doc__, serial=serial, num_args=num_args,
                       kwarg_names=kwarg_names)
        return entry
    return wrap


@capability('test', 'Test Capability', num_args=2)
def cap1(a, b):
    """
    Add a and b
    :param a: int
    :param b: int
    :return: result
    """
    return a + b


if __name__ == '__main__':
    print runtime_capabilities['test']
    print runtime_capabilities['test']['doc']
    print runtime_capabilities['test']['entry'](1, 2)
