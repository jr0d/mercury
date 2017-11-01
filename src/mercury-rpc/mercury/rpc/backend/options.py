from mercury.common.configuration import MercuryConfiguration

from mercury.rpc.configuration import add_common_options, RPC_CONFIG_FILE


def parse_options():
    configuration = MercuryConfiguration(
        'mercury-backend',
        RPC_CONFIG_FILE,
        description='The mercury backend RPC service'
    )

    add_common_options(configuration)

    configuration.add_option('rpc.backend.bind_address',
                             default='tcp://127.0.0.1:9002',
                             help_string='Backend service bind address')

    configuration.add_option('rpc.origin.name',
                             default='local',
                             help_string='Name identifier of the backend '
                                         'service')

    configuration.add_option('rpc.origin.datacenter',
                             default='local1',
                             help_string='The datacenter which the backend is '
                                         'running')

    configuration.add_option('rpc.origin.public_address',
                             default='localhost',
                             help_string='The address to publish')

    configuration.add_option('rpc.origin.frontend_port',
                             default=9001,
                             special_type=int,
                             help_string='The port to publish')

    configuration.add_option('rpc.inventory_router',
                             default='tcp://localhost:9000',
                             help_string='Inventory router url')

    configuration.add_option('asyncio_debug',
                             '--asyncio-debug',
                             'ASYNCIO_DEBUG',
                             'logging.debug_asyncio',
                             default=False,
                             special_type=bool,
                             help_string='Enable asyncio debugging'
                             )

    configuration.add_option('subtask_debug',
                             '--subtask-debug',
                             'SUBTASK_DEBUG',
                             'logging.debug_subtasks',
                             default=False,
                             special_type=bool,
                             help_string='Enable subtasks (ping, monitor) '
                                         'debugging'
                             )

    configuration.add_option('rpc.ping.interval',
                             default=30,
                             special_type=int,
                             help_string='Interval between ping requests')

    configuration.add_option('rpc.ping.cycle_time',
                             default=10,
                             special_type=int,
                             help_string='Time between ping sweep loops')

    configuration.add_option('rpc.ping.initial_timeout',
                             default=2500,
                             special_type=int,
                             help_string='Initial timeout in milliseconds')

    configuration.add_option('rpc.ping.retries',
                             default=5,
                             special_type=int,
                             help_string='Number of times to retry')

    configuration.add_option('rpc.ping.backoff',
                             default=0.42,
                             special_type=float,
                             help_string='Exponential backoff modifier')

    return configuration.scan_options()
