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

from mercury.common.configuration import MercuryConfiguration

INVENTORY_CONFIG_FILE = 'mercury-inventory.yaml'


def options(configuration):
    """ A single place to add program options """

    configuration.add_option('inventory.bind_address',
                             default='tcp://localhost:9000',
                             help_string='The address to bind to'
                             )

    configuration.add_option('asyncio_debug',
                             '--asyncio-debug',
                             'ASYNCIO_DEBUG',
                             'logging.debug_asyncio',
                             default=False,
                             special_type=bool,
                             help_string='Enable asyncio debugging'
                             )

    configuration.add_option('inventory.db.name',
                             default='test',
                             help_string='The database for our collections')

    configuration.add_option('inventory.db.collection',
                             default='inventory',
                             help_string='The collection for our documents')

    configuration.add_option('inventory.db.servers',
                             default='localhost:27017',
                             special_type=list,
                             help_string='Server or coma separated list of '
                                         'servers to connect to')

    configuration.add_option('inventory.db.replica_name',
                             config_address='inventory.db.replica_name',
                             help_string='An optional replica')


def get_inventory_configuration():
    inventory_configuration = MercuryConfiguration('mercury-inventory',
                                                   INVENTORY_CONFIG_FILE)
    options(inventory_configuration)

    return inventory_configuration.scan_options()
