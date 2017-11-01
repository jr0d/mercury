# Copyright 2017 Ruben Quinones (ruben.quinones@rackspace.com)
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


log = logging.getLogger(__name__)


class HookException(Exception):
    pass


class Hook(object):
    """
    Base Hook class. Hooks provide a way to manage inventory data before or
    after it is inserted or updated in the database and run additional 
    processes if needed.
    """

    def __init__(self, data, *args, **kwargs):
        self.data = data

    def run(self):
        pass


class InterfaceHook(Hook):
    """
    Interface data handler, this should run when updating interface data for
    a given inventory record.
    """

    def process_data(self):
        """
        Convert interface data to mongodb dot notation in order to update the 
        inventory record without erasing data collected asynchronously.
        """
        interfaces = self.data.pop('interfaces', [])
        for i, interface in enumerate(interfaces):
            for key, value in interface.items():
                new_key = 'interfaces.{}.{}'.format(i, key)
                self.data[new_key] = value

    def run(self):
        self.process_data()


class LLDPHook(Hook):
    """
    Interface LLDP data handler, this should run when updating LLDP data for
    a given inventory interface.
    """

    def process_data(self):
        """
        Convert interface LLDP data to mongodb dot notation in order to update
        the interface specified by the 'interface_index' key.
        """
        try:
            lldp = self.data.pop('lldp')
            interface_index = lldp.pop('interface_index')
        except KeyError:
            raise HookException('Missing LLDP data')
        lldp_key = 'interfaces.{}.lldp'.format(interface_index)
        self.data[lldp_key] = lldp

    def run(self):
        self.process_data()


HOOK_MAP = {
    'interfaces': InterfaceHook,
    'lldp': LLDPHook,
}


def run_hooks(hooks, data):
    """
    Calls the run method for each hook in the hooks dict.
    
    :param hooks: A dict of keys/hook classes
    :param data: Inventory data dict
    :return: 
    """
    for hook_key, hook_class in hooks.items():
        hook = hook_class(data)
        log.info('Running {} hook'.format(hook_key))
        hook.run()


def get_hooks_from_data(data):
    """
    Returns a dict of hooks based on the keys present in the data dict
    
    :param data: Inventory data dict
    :return: dict 
    """
    keys = set(data.keys()) & set(HOOK_MAP.keys())
    hooks = {key: HOOK_MAP[key] for key in keys}
    return hooks
