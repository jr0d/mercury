# Copyright 2015 Jared Rodriguez (jared.rodriguez@rackspace.com)
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


def add_capability(entry, name, description, doc=None, serial=False, num_args=None, kwarg_names=None, no_return=False,
                   dependency_callback=None, timeout=1800):
    LOG.info('Adding capability %s' % name)
    runtime_capabilities[name] = {
        'name': name,
        'entry': entry,
        'description': description,
        'doc': doc,
        'serial': serial,
        'num_args': num_args,
        'kwarg_names': kwarg_names,
        'no_return': no_return,
        'dependency_callback': dependency_callback,
        'timeout': timeout
    }


def capability(name, description, serial=False, num_args=None, kwarg_names=None, no_return=False,
               dependency_callback=None, timeout=1800):
    def wrap(entry):
        add_capability(entry, name, description, doc=entry.__doc__, serial=serial, num_args=num_args,
                       kwarg_names=kwarg_names, no_return=no_return, dependency_callback=dependency_callback,
                       timeout=timeout)
        return entry
    return wrap

