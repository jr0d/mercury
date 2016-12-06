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
import time

from mercury.agent.capabilities import capability
from mercury.agent.configuration import remote_configuration
from mercury.press.entry import entry

log = logging.getLogger(__name__)


def add_mercury_plugin_data(press_configuration, task_id):
    temp_plugins = press_configuration.get('plugins', [])
    if 'mercury' not in temp_plugins:
        temp_plugins.append('mercury')
        press_configuration['plugins'] = temp_plugins

    press_configuration['mercury'] = {
        'task_id': task_id,
        'backend_zurl': remote_configuration['rpc_service']
    }


@capability('press', description='Native press support in mercury', serial=True,
            kwarg_names=['configuration'], task_id_kwargs=True)
def press_native(**kwargs):
    press_configuration = kwargs['configuration']
    task_id = kwargs['task_id']

    add_mercury_plugin_data(press_configuration, task_id)

    log.info('Starting press')
    start = time.time()
    entry(press_configuration)
    return {'press_execution_time': time.time() - start}
