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
from mercury.common.inventory_client import InventoryClient

__all__ = ['AGENT_CONFIG_FILE', 'agent_configuration']

# Private
__backend_client = None

log = logging.getLogger(__name__)

# Helpers
AGENT_CONFIG_FILE = 'mercury-agent.yaml'
agent_configuration = get_configuration(AGENT_CONFIG_FILE)
remote_configuration = agent_configuration.get('remote', {})

try:
    inventory_url = remote_configuration['inventory_service']
except KeyError:
    log.warning('Missing inventory service url')


def get_backend_client():
    # TODO: Trying this out, 0mq says it is ok
    global __backend_client
    if not __backend_client:
        __backend_client = InventoryClient(inventory_url)
    return __backend_client
