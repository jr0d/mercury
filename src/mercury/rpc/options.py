from mercury.common.configuration import MercuryConfiguration


DEFAULT_CONFIG_FILE = 'mercury-rpc.yaml'


def parse_options():
    configuration = MercuryConfiguration(
        'mercury-rcp',
        DEFAULT_CONFIG_FILE,
        description='The mercury RPC service'
    )

    configuration.add_option('rpc.bind_address',
                             default='tcp://127.0.0.1:9001',
                             help_string='Mercury RPC bind address')

    configuration.add_option('asyncio_debug',
                             '--asyncio-debug',
                             'ASYNCIO_DEBUG',
                             'logging.debug_asyncio',
                             default=False,
                             special_type=bool,
                             help_string='Enable asyncio debugging'
                             )

    configuration.add_option('rpc.inventory_router',
                             default='tcp://localhost:9000',
                             help_string='Inventory router url')

    configuration.add_option('subtask_debug',
                             '--subtask-debug',
                             'SUBTASK_DEBUG',
                             'logging.debug_subtasks',
                             default=False,
                             special_type=bool,
                             help_string='Enable subtasks (ping, monitor) '
                                         'debugging'
                             )

    configuration.add_option('rpc.database.servers',
                             default='127.0.0.1:27017',
                             special_type=list,
                             help_string='Server or coma separated list of '
                                         'servers to connect to')

    configuration.add_option('rpc.database.name',
                             default='test',
                             help_string='The database for our collections')

    configuration.add_option('rpc.database.replica_name',
                             config_address='rpc.database.replica_name',
                             help_string='Optional replicaset name')

    configuration.add_option('rpc.database.jobs_collection',
                             config_address='rpc.database.jobs_collection',
                             default='rpc_jobs',
                             help_string='The collection for RPC jobs')

    configuration.add_option('rpc.database.tasks_collection',
                             config_address='rpc.database.tasks_collection',
                             default='rpc_tasks',
                             help_string='The collection for RPC tasks')

    configuration.add_option('rpc.database.username',
                             help_string="The database user")

    configuration.add_option('rpc.database.password',
                             help_string="The database use password")

    return configuration.scan_options()
