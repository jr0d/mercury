# Copyright 2018 Ruben Quinones (ruben.quinones@rackspace.com)
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

from mercury.common.configuration import MercuryConfiguration

BOOT_CONFIG_FILE = 'mercury-boot.yaml'


def options(configuration):
    """ A single place to add program options """

    configuration.add_option(
        'host',
        env_variable='MBOOT_HOST',
        default='127.0.0.1',
        help_string='The host address to bind to')

    configuration.add_option(
        'port',
        env_variable='MBOOT_PORT',
        default=5000,
        special_type=int,
        help_string='The port to bind to')

    configuration.add_option(
        'inventory.inventory_router',
        '--inventory-router',
        default='tcp://127.0.0.1:9000',
        help_string='The inventory router url')

    configuration.add_option(
        'logging.log_file',
        default='mercury-boot.log',
        help_string='The log file path')

    configuration.add_option(
        'logging.level', default='DEBUG', help_string='The app log level')

    configuration.add_option(
        'agent.file_server_url',
        required=True,
        help_string='The file server path containing agent boot files')

    configuration.add_option(
        'agent.kernel',
        default='vmlinuz',
        help_string='The agent kernel')

    configuration.add_option(
        'agent.initrd',
        default='initrd',
        help_string='The agent initial ram file system')

    configuration.add_option(
        'agent.rootfs_option',
        help_string='The kernel command line option used by the initrd to find '
                    'the root file system',
        required=True
    )

    configuration.add_option(
        'agent.file_system',
        default='mercury-agent.sqfs',
        help_string='The agent file system'
    )

    configuration.add_option(
        'agent.kernel_options',
        default='',
        help_string='Kernel options for the agent environment'
    )


def get_boot_configuration():
    boot_configuration = MercuryConfiguration('mercury-boot', BOOT_CONFIG_FILE)
    options(boot_configuration)

    return boot_configuration.scan_options()
