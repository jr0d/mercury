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
        default='127.0.0.1',
        help_string='The host address to bind to')

    configuration.add_option(
        'port',
        default=5000,
        help_string='The port to bind to')

    configuration.add_option(
        'file_upload_directory',
        default='/var/www/mercury-boot',
        help_string='The file upload directory')

    configuration.add_option(
        'default_boot_file',
        default='pxelinux.0',
        help_string='Default boot file path')

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


def get_boot_configuration():
    boot_configuration = MercuryConfiguration('mercury-boot', BOOT_CONFIG_FILE)
    options(boot_configuration)

    return boot_configuration.scan_options()
