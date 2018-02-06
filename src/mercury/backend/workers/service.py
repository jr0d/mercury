import logging

from mercury.common.configuration import MercuryConfiguration
from mercury.common.task_managers.base.manager import Manager
from mercury.common.task_managers.redis.task import RedisTask
from mercury.common.clients.router_req_client import RouterReqClient

from mercury.backend.rpc_client import RPCClient
from mercury.backend.configuration import (
    add_common_options, BACKEND_CONFIG_FILE
)

log = logging.getLogger(__name__)


def options():
    configuration = MercuryConfiguration(
        'mercury-rpc-worker',
        BACKEND_CONFIG_FILE,
        description='Manager process for RPC workers'
    )

    add_common_options(configuration)

    configuration.add_option('backend.redis.host',
                             default='localhost',
                             help_string='Redis server address')

    configuration.add_option('backend.redis.port',
                             default=6379,
                             special_type=int,
                             help_string='Redis server port')

    configuration.add_option('backend.redis.queue',
                             default='rpc_task_queue',
                             help_string='The queue to use for RPC tasks')

    configuration.add_option('backend.workers.threads',
                             special_type=int,
                             default=4)

    configuration.add_option('backend.workers.max_requests_per_thread',
                             special_type=int,
                             default=100)

    configuration.add_option('backend.rpc_router',
                             required=True,
                             help_string='The RPC service router')

    return configuration.scan_options()


class RPCTask(RedisTask):
    def __init__(self, rpc_router_url, redis_host, redis_port, redis_queue):
        """

        :param rpc_router_url:
        :param redis_host:
        :param redis_port:
        :param redis_queue:
        """
        self.rpc_router_url = rpc_router_url
        self.rpc_router = RPCClient(self.rpc_router_url,
                                    linger=0,
                                    response_timeout=5,
                                    rcv_retry=3)
        super(RPCTask, self).__init__(redis_host, redis_port, redis_queue)

    def do(self):
        url = 'tcp://{host}:{port}'.format(**self.task)
        client = RouterReqClient(url, linger=0,
                                 response_timeout=5,
                                 rcv_retry=3)

        client.service_name = 'AgentTaskService'

        _payload = {
            'category': 'rpc',
            'method': self.task['method'],
            'args': self.task['args'],
            'kwargs': self.task['kwargs'],
            'task_id': self.task['task_id'],
            'job_id': self.task['job_id']
        }
        log.info(f'Dispatching task: {self.task}')
        response = client.transceiver(_payload)
        if response.get('error'):  # Transport Error
            err_msg = f'{self.task["mercury_id"]} has gone away while ' \
                      f'handling {self.task["task_id"]}. Transport Message: ' \
                      f'{response["message"]}'
            log.error(err_msg)
            self.rpc_router.complete_task({
                'job_id': self.task['job_id'],
                'task_id': self.task['task_id'],
                'status': 'ERROR',
                'message': err_msg,
            })
        elif response['message']['status'] != 0:
            self.rpc_router.complete_task({
                'job_id': self.task['job_id'],
                'task_id': self.task['task_id'],
                'status': 'ERROR',
                'message': f'Dispatch Error: {response["message"]}'})

        # close the socket
        client.close()


def configure_logging(config):
    logging.basicConfig(level=logging.getLevelName(config.logging.level),
                        format=config.logging.format)


def main():
    config = options()

    configure_logging(config)

    # Set this up for access from our threads

    manager = Manager(RPCTask, config.backend.workers.threads,
                      config.backend.workers.max_requests_per_thread,
                      handler_args=(config.backend.rpc_router,
                                    config.backend.redis.host,
                                    config.backend.redis.port,
                                    config.backend.redis.queue))
    manager.manage()


if __name__ == '__main__':
    main()
