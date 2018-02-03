from mercury.common.configuration import MercuryConfiguration

DEFAULT_CONFIG_FILE = 'mercury-inventory.yaml'


def parse_options():
    configuration = MercuryConfiguration(
        'mercury-inventory',
        DEFAULT_CONFIG_FILE,
        description='The mercury inventory service'
    )

    configuration.add_option('inventory.bind_address',
                             default='tcp://127.0.0.1:9000',
                             help_string='Mercury Inventory bind address'
                             )

    configuration.add_option('asyncio_debug',
                             '--asyncio-debug',
                             'ASYNCIO_DEBUG',
                             'logging.debug_asyncio',
                             default=False,
                             special_type=bool,
                             help_string='Enable asyncio debugging'
                             )

    configuration.add_option('inventory.database.name',
                             default='test',
                             help_string='The inventory database')

    configuration.add_option('inventory.database.collection',
                             default='inventory',
                             help_string='The collection for inventory '
                                         'documents')

    configuration.add_option('inventory.database.servers',
                             default='localhost:27017',
                             special_type=list,
                             help_string='Server or coma separated list of '
                                         'servers to connect to')

    configuration.add_option('inventory.database.replica_name',
                             help_string='An optional replica name')

    configuration.add_option('inventory.database.username',
                             help_string='The database user')

    configuration.add_option('inventory.database.password',
                             help_string='The database user\'s password')

    return configuration.scan_options()
