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

from mercury.common.configuration import get_configuration
from mercury.common.exceptions import MercuryConfigurationError

__all__ = ['AGENT_CONFIG_FILE', 'agent_configuration']


log = logging.getLogger(__name__)

# Helpers
DEFAULT_AGENT_CONFIG_FILE = 'mercury-agent.yaml'


agent_configuration = {}
remote_configuration = {}


def set_agent_configuration(namespace):
    global agent_configuration
    global remote_configuration
    configuration_file = namespace.config_file or DEFAULT_AGENT_CONFIG_FILE
    agent_configuration.update(**get_configuration(configuration_file))
    if not agent_configuration:
        raise MercuryConfigurationError('Configuration file is missing')
    if namespace.debug:
        logging.basicConfig(level=logging.DEBUG)
        log.info('Setting log level to DEBUG')
        agent_configuration.get('agent', {})['log_level'] = 'DEBUG'

    remote_configuration.update(**agent_configuration['remote'])
