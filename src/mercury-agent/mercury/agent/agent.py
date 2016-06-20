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

"""
agent:

    1) Start Pong service
    2) Start RPC service
    2) Register

#PROTOTYPE

"""

import argparse
import logging

from mercury.agent.capabilities import runtime_capabilities
from mercury.agent.configuration import agent_configuration
from mercury.agent.pong import spawn_pong_process
from mercury.agent.register import get_dhcp_ip, register
from mercury.agent.rpc import AgentService
from mercury.common.exceptions import MercuryCritical
from mercury.common.inventory_client.client import InventoryClient
from mercury.inspector import inspect


log = logging.getLogger(__name__)


def spawn_agent(dhcp_ip_method='simple'):
    """
    Prototype agent service entry
    :param dhcp_ip_method: method to get dhcp
    :return:
    """

    local_config = agent_configuration.get('agent', {})
    remote_config = agent_configuration.get('remote', {})
    agent_bind_address = local_config.get('service_bind_address', 'tcp://0.0.0.0:9003')
    pong_bind_address = local_config.get('pong_bind_address', 'tcp://0.0.0.0:9004')

    inventory_url = remote_config.get('inventory_service')

    if not inventory_url:
        raise MercuryCritical('Inventory service URL is not specified')

    rpc_backend = agent_configuration.get('remote', {}).get('rpc_service')

    if not rpc_backend:
        raise MercuryCritical('Missing rpc backend in local configuration')

    log.debug('agent: %s, pong: %s, inventory_remote: %s' % (agent_bind_address,
                                                             pong_bind_address,
                                                             inventory_url))

    log.info('Running inspectors')

    device_info = inspect.inspect()

    log.info('Registering device inventory')

    inventory_client = InventoryClient(inventory_url)
    object_id = inventory_client.update(device_info)

    log.debug('Created record: %s' % object_id)

    log.info('Starting pong service')
    spawn_pong_process(pong_bind_address)

    log.info('Registering device')
    local_ip = get_dhcp_ip(device_info, method=dhcp_ip_method)
    local_ipv6 = None
    register(rpc_backend, device_info['mercury_id'], local_ip, local_ipv6, runtime_capabilities)

    log.info('Starting agent rpc service: %s' % agent_bind_address)
    agent_service = AgentService(agent_bind_address, rpc_backend)
    agent_service.bind()
    agent_service.start()


def _parse_args():
    parser = argparse.ArgumentParser(description='Mercury Agent')


def main():
    logging.basicConfig(level=logging.DEBUG)
    fh = logging.FileHandler('mercury-agent.log')
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    mercury_logger = logging.getLogger('mercury')
    mercury_logger.addHandler(fh)
    mercury_logger.info('[prototype] starting agent')
    logging.getLogger('mercury.agent.pong').setLevel(logging.DEBUG)

    spawn_agent('simple')


if __name__ == '__main__':
    main()
