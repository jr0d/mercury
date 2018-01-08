from mercury.common.configuration import MercuryConfiguration

from mercury.backend.configuration import add_common_options, \
    BACKEND_CONFIG_FILE


def parse_options():
    configuration = MercuryConfiguration(
        'mercury-backend',
        BACKEND_CONFIG_FILE,
        description='The mercury backend RPC backend'
    )

    add_common_options(configuration)

    configuration.add_option('backend.agent_service.bind_address',
                             default='tcp://127.0.0.1:9002',
                             help_string='Backend backend bind address')

    configuration.add_option('backend.origin.name',
                             default='local',
                             help_string='Name identifier of the backend '
                                         'backend')

    configuration.add_option('backend.origin.datacenter',
                             default='local1',
                             help_string='The datacenter which the backend is '
                                         'running')

    configuration.add_option('backend.origin.queue_service_vip',
                             default='localhost',
                             help_string='The address to publish')

    configuration.add_option('backend.origin.queue_service_port',
                             default=9007,
                             special_type=int,
                             help_string='The port to publish')

    configuration.add_option('backend.inventory_router',
                             required=True,
                             help_string='Inventory router url')

    configuration.add_option('backend.rpc_router',
                             required=True,
                             help_string='RPC router url')

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

    configuration.add_option('backend.ping.interval',
                             default=30,
                             special_type=int,
                             help_string='Interval between ping requests')

    configuration.add_option('backend.ping.cycle_time',
                             default=10,
                             special_type=int,
                             help_string='Time between ping sweep loops')

    configuration.add_option('backend.ping.initial_timeout',
                             default=2500,
                             special_type=int,
                             help_string='Initial timeout in milliseconds')

    configuration.add_option('backend.ping.retries',
                             default=5,
                             special_type=int,
                             help_string='Number of times to retry')

    configuration.add_option('backend.ping.backoff',
                             default=0.42,
                             special_type=float,
                             help_string='Exponential backoff modifier')

    return configuration.scan_options()
