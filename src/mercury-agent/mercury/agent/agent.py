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

import argparse
import logging

from mercury.agent.capabilities import runtime_capabilities
from mercury.agent.configuration import agent_configuration, set_agent_configuration
from mercury.agent.pong import spawn_pong_process
from mercury.agent.register import get_dhcp_ip, register
from mercury.agent.remote_logging import MercuryLogHandler
from mercury.agent.rpc import AgentService
from mercury.common.clients.rpc.backend import BackEndClient
from mercury.common.exceptions import MercuryCritical, MercuryGeneralException
from mercury.inspector import inspect

# Async Inspectors

from mercury.inspector.inspectors.async_inspectors.lldp import LLDPInspector


log = logging.getLogger(__name__)


class Agent(object):
    def __init__(self, configuration, logger):
        """

        :param configuration:
        """
        self.configuration = configuration
        self.local_config = self.configuration.get('agent', {})
        self.remote_config = self.configuration.get('remote', {})
        self.agent_bind_address = self.local_config.get('service_bind_address', 'tcp://0.0.0.0:9003')
        self.pong_bind_address = self.local_config.get('pong_bind_address', 'tcp://0.0.0.0:9004')

        self.rpc_backend_url = agent_configuration.get('remote', {}).get('rpc_service')
        self.log_handler = logger

        if not self.rpc_backend_url:
            raise MercuryCritical('Missing rpc backend in local configuration')

        self.backend = BackEndClient(self.rpc_backend_url)

    def run(self, dhcp_ip_method='simple'):
        # TODO: Add other mechanisms for enumerating the devices public ip
        log.debug('Agent: %s, Pong: %s' % (self.agent_bind_address,
                                           self.pong_bind_address))

        log.info('Running inspectors')

        device_info = inspect.inspect()

        log.info('Registering device inventory for MercuryID {}'.format(device_info['mercury_id']))

        log.info('Starting pong service')
        spawn_pong_process(self.pong_bind_address)

        log.info('Registering device')
        if self.local_config.get('local_ip'):
            # This allows us to explicitly set the agent ip. This is useful for testing in environments which
            # utilize containers which are not directly accessible via a discoverable ip address.
            # This option will be implemented as a command line argument in the future.
            local_ip = self.local_config['local_ip']
        else:
            local_ip = get_dhcp_ip(device_info, method=dhcp_ip_method)

        # TODO: enumerate ipv6 addresses
        local_ipv6 = None

        register(self.backend, device_info, local_ip, local_ipv6, runtime_capabilities)

        # LogHandler

        log.info('Injecting MercuryID for remote logging')
        self.log_handler.set_mercury_id(device_info['mercury_id'])
        log.info('Injection completed')

        # AsyncInspectors
        try:
            LLDPInspector(device_info, self.backend).inspect()
        except MercuryGeneralException as mge:
            log.error('Caught recoverable exception running async inspector: {}'.format(mge))

        log.info('Starting agent rpc service: %s' % self.agent_bind_address)

        agent_service = AgentService(self.agent_bind_address, self.rpc_backend_url)
        agent_service.bind()
        agent_service.start()


def parse_args():
    parser = argparse.ArgumentParser(description='Mercury Agent')
    parser.add_argument('-c', '--config-file', default=None, help='Path to agent configuration file')
    parser.add_argument('-d', '--debug', default=False, action='store_true', help='Enable debug logging')
    return parser.parse_args()


def setup_logging():
    log_level = logging.getLevelName(agent_configuration['agent']['log_level'])
    logging.basicConfig(level=log_level)
    fh = logging.FileHandler(agent_configuration['agent']['log_file'])

    fh.setLevel(log_level)
    formatter = logging.Formatter(agent_configuration['agent']['log_format'])
    fh.setFormatter(formatter)

    mercury_logger = logging.getLogger('mercury')
    mercury_logger.addHandler(fh)
    mercury_logger.info('Starting Agent')

    # Quiet these down
    logging.getLogger('mercury.agent.pong').setLevel(logging.ERROR)
    logging.getLogger('hpssa._cli').setLevel(logging.ERROR)

    # Configure the remote logging handler
    mh = MercuryLogHandler(agent_configuration.get('remote', {}).get('log_service'))
    mercury_logger.addHandler(mh)

    # Return this so that we can inject the mercury_id once we have it
    return mh


def merge_configuration(namespace):
    set_agent_configuration(namespace)


def main():
    namespace = parse_args()
    merge_configuration(namespace)

    mercury_handler = setup_logging()
    agent = Agent(agent_configuration, mercury_handler)
    agent.run('simple')


if __name__ == '__main__':
    main()
