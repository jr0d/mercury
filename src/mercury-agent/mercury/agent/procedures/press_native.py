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
from mercury.agent.client import BackEndClient
from mercury.agent.configuration import agent_configuration, remote_configuration

from mercury.common.exceptions import fancy_traceback_short, parse_exception

# PyCharm does not like press anymore for some reason.. too many names
# noinspection PyUnresolvedReferences
from press.main import Press

# noinspection PyUnresolvedReferences
from press.plugin_init import init_plugins

log = logging.getLogger(__name__)


# noinspection PyBroadException
def entry(press_configuration):
    log.info('Initializing plugins')

    plugin_dirs = agent_configuration.get('press', {}).get('plugin_dirs')

    init_plugins(press_configuration, plugin_dirs)

    return_data = {}

    p = None
    try:
        p = Press(press_configuration)
    except Exception:
        exec_dict = parse_exception()
        log.error('Error during initialization: {}'.format(
            fancy_traceback_short(exec_dict)))
        return_data = {'error': True, 'message': 'Error during initialization', 'exception': exec_dict}

    if p:
        try:
            p.run()
        except Exception:
            exec_dict = parse_exception()
            log.error('Error during deployment: {}'.format(
                fancy_traceback_short(exec_dict)))
            return_data = {'error': True, 'message': 'Error during initialization', 'exception': exec_dict}
        finally:
            if p.layout.committed:
                time.sleep(2)
                p.teardown()

            # Clear logging handlers!
            del logging.getLogger('press').handlers[:]  # python2 doesn't have list.clear()

    return return_data


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

    backend_client = BackEndClient(remote_configuration['rpc_service'])
    log.info('Starting press')
    start = time.time()
    backend_client.task_update({'task_id': task_id, 'action': 'Press: Launching'})
    return_data = entry(press_configuration)
    return_data['press_execution_time'] = time.time() - start
    return return_data
