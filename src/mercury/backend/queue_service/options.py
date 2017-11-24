from mercury.common.configuration import MercuryConfiguration

from mercury.backend.configuration import BACKEND_CONFIG_FILE


def parse_options():
    configuration = MercuryConfiguration(
        'mercury-queue-backend',
        BACKEND_CONFIG_FILE,
        description='Mercury backend queue service'
    )

    configuration.add_option('backend.queue_service.bind_address',
                             default='tcp://127.0.0.1:9007',
                             help_string='Queue backend bind address')

    configuration.add_option('backend.redis.host',
                             default='localhost',
                             help_string='Redis server address')

    configuration.add_option('backend.redis.port',
                             default='6379',
                             special_type=int,
                             help_string='Redis server port')

    configuration.add_option('backend.redis.queue',
                             default='rpc_task_queue',
                             help_string='The queue to use for RPC tasks')

    configuration.add_option('backend.inventory_router',
                             default='tcp://localhost:9000',
                             help_string='Inventory router url')

    return configuration.scan_options()
