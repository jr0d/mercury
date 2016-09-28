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
from mercury.common.exceptions import MercuryCritical, MercuryGeneralException
from mercury.common.inventory_client.client import InventoryClient
from mercury.inspector import inspect

# Async Inspectors

from mercury.inspector.inspectors.async_inspectors.lldp import LLDPInspector


log = logging.getLogger(__name__)


class Agent(object):
    def __init__(self, configuration):
        self.configuration = configuration
        self.local_config = self.configuration.get('agent', {})
        self.remote_config = self.configuration.get('remote', {})
        self.agent_bind_address = self.local_config.get('service_bind_address', 'tcp://0.0.0.0:9003')
        self.pong_bind_address = self.local_config.get('pong_bind_address', 'tcp://0.0.0.0:9004')

        self.inventory_url = self.remote_config.get('inventory_service')

        if not self.inventory_url:
            raise MercuryCritical('Inventory service URL is not specified')

        self.rpc_backend = agent_configuration.get('remote', {}).get('rpc_service')

        if not self.rpc_backend:
            raise MercuryCritical('Missing rpc backend in local configuration')

    def run(self, dhcp_ip_method='simple'):
        log.debug('Agent: %s, Pong: %s, Inventory: %s' % (self.agent_bind_address,
                                                          self.pong_bind_address,
                                                          self.inventory_url))

        log.info('Running inspectors')

        device_info = inspect.inspect()

        log.info('Registering device inventory for MercuryID {}'.format(device_info['mercury_id']))

        inventory_client = InventoryClient(self.inventory_url)
        object_id = inventory_client.insert_one(device_info)

        log.debug('Created/Updated inventory record: %s' % object_id)

        log.info('Starting pong service')
        spawn_pong_process(self.pong_bind_address)

        log.info('Registering device')
        local_ip = get_dhcp_ip(device_info, method=dhcp_ip_method)
        local_ipv6 = None
        register(self.rpc_backend, device_info['mercury_id'], local_ip, local_ipv6, runtime_capabilities)

        # AsyncInspectors
        try:
            LLDPInspector(device_info, inventory_client).inspect()
        except MercuryGeneralException as mge:
            log.error('Caught recoverable exception running async inspector: {}'.format(mge))

        log.info('Starting agent rpc service: %s' % self.agent_bind_address)

        agent_service = AgentService(self.agent_bind_address, self.rpc_backend)
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
    logging.getLogger('hpssa._cli').setLevel(logging.ERROR)

    agent = Agent(agent_configuration)
    agent.run('simple')


if __name__ == '__main__':
    main()
