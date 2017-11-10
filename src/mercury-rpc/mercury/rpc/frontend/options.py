from mercury.common.configuration import MercuryConfiguration

from mercury.rpc.configuration import add_common_options, RPC_CONFIG_FILE


def parse_options():
    configuration = MercuryConfiguration(
        'mercury-frontend',
        RPC_CONFIG_FILE,
        description='The mercury frontend RPC service'
    )

    add_common_options(configuration)

    configuration.add_option('rpc.frontend.bind_address',
                             default='tcp://127.0.0.1:9002',
                             help_string='Backend service bind address')

    configuration.add_option('rpc.redis.host',
                             default='localhost',
                             help_string='Redis server address')

    configuration.add_option('rpc.redis.port',
                             default='6379',
                             special_type=int,
                             help_string='Redis server port')

    configuration.add_option('rpc.redis.queue',
                             default='rpc_task_queue',
                             help_string='The queue to use for RPC tasks')

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
                             'subtask_DEBUG',
                             'logging.debug_subtasks',
                             default=False,
                             special_type=bool,
                             help_string='Enable subtasks (ping, monitor) '
                                         'debugging'
                             )

    return configuration.scan_options()
