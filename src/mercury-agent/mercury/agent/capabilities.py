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


def add_capability(entry, name, description, doc=None, serial=False,
                   num_args=None, kwarg_names=None, no_return=False,
                   dependency_callback=None, timeout=1800,
                   task_id_kwargs=False):
    """Add a new capability to the runtime capabilities.

    :param entry: The new capability.
    :param name: Name of the new capability.
    :param description: Description of the new capability.
    :param doc: Function docstring.
    :param serial: Boolean indication if the task is serial.
    :param num_args: Number of expected arguments.
    :param kwarg_names: Named arguments.
    :param no_return: True if the task doesn't return any value.
    :param dependency_callback: Callback to check dependency.
    :param timeout: Timeout for the new capability.
    :param task_id_kwargs: Whether to put task_id in kwargs.
    """
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
        'timeout': timeout,
        'task_id_kwargs': task_id_kwargs
    }


def capability(name, description, serial=False, num_args=None,
               kwarg_names=None, no_return=False,
               dependency_callback=None, timeout=1800, task_id_kwargs=False):
    """Decorator to add a new capability.

    :param name: Name of the new capability.
    :param description: Description of the new capability.
    :param serial: Boolean indication if the task is serial.
    :param num_args: Number of expected arguments.
    :param kwarg_names: Named arguments.
    :param no_return: True if the task doesn't return any value.
    :param dependency_callback: Callback to check dependency.
    :param timeout: Timeout for the new capability.
    :param task_id_kwargs: Whether to put task_id in kwargs.
    """
    def wrap(entry):
        add_capability(entry, name, description, doc=entry.__doc__,
                       serial=serial, num_args=num_args,
                       kwarg_names=kwarg_names, no_return=no_return,
                       dependency_callback=dependency_callback,
                       timeout=timeout, task_id_kwargs=task_id_kwargs)
        return entry
    return wrap
