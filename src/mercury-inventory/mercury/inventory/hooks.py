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


log = logging.getLogger(__name__)


class HookException(Exception):
    pass


class Hook(object):

    def __init__(self, data):
        self.data = data

    async def run(self):
        pass


class InterfaceHook(Hook):

    async def process_data(self):
        interfaces = self.data.pop('interfaces', [])
        for i, interface in enumerate(interfaces):
            for key, value in interface.items():
                new_key = 'interfaces.{}.{}'.format(i, key)
                self.data[new_key] = value

    async def run(self):
        await self.process_data()


class LLDPHook(Hook):

    async def process_data(self):
        try:
            lldp = self.data.pop('lldp')
            interface_index = lldp.pop('interface_index')
        except KeyError:
            raise HookException('Missing LLDP data')
        lldp_key = 'interfaces.{}.lldp'.format(interface_index)
        self.data[lldp_key] = lldp

    async def run(self):
        await self.process_data()


HOOK_MAP = {
    'interfaces': InterfaceHook,
    'lldp': LLDPHook,
}


async def run_hooks(hooks, data):
    for hook_key, hook_class in hooks.items():
        hook = hook_class(data)
        log.info('Running {} hook'.format(hook_key))
        await hook.run()


async def get_hooks_from_data(data):
    keys = set(data.keys()) & set(HOOK_MAP.keys())
    hooks = {key: HOOK_MAP[key] for key in keys}
    return hooks