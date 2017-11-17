import logging

from mercury.common.configuration import MercuryConfiguration
from mercury.common.task_managers.base.manager import Manager
from mercury.common.task_managers.redis.task import RedisTask
from mercury.common.transport import SimpleRouterReqClient
from mercury.rpc.jobs.tasks import update_task, complete_task
from mercury.rpc.configuration import add_common_options, RPC_CONFIG_FILE
from mercury.rpc.mongo import RPCCollectionFactory


# TODO: Ditch this threadpool implementation and use the event loop
# TODO: Research redis asyncio library

log = logging.getLogger(__name__)


config = None


def options():
    configuration = MercuryConfiguration(
        'mercury-rpc-worker',
        RPC_CONFIG_FILE,
        description='Manager process for RPC workers'
    )

    add_common_options(configuration)

    configuration.add_option('rpc.redis.host',
                             default='localhost',
                             help_string='Redis server address')

    configuration.add_option('rpc.redis.port',
                             default=6379,
                             special_type=int,
                             help_string='Redis server port')

    configuration.add_option('rpc.redis.queue',
                             default='rpc_task_queue',
                             help_string='The queue to use for RPC tasks')

    configuration.add_option('rpc.worker.threads',
                             special_type=int,
                             default=4)

    configuration.add_option('rpc.worker.max_requests_per_thread',
                             special_type=int,
                             default=100)

    return configuration.scan_options()

class RPCTask(RedisTask):
    def do(self):
        url = 'tcp://{host}:{port}'.format(**self.task)
        client = SimpleRouterReqClient(url)
        _payload = {
            'category': 'rpc',
            'method': self.task['method'],
            'args': self.task['args'],
            'kwargs': self.task['kwargs'],
            'task_id': self.task['task_id'],
            'job_id': self.task['job_id']
        }
        log.debug('Dispatching task: %s' % self.task)
        # Status insert happens before dispatch because the task COULD complete
        # before write due to connection overhead
        update_task(self.task['task_id'], {'status': 'DISPATCHING'})
        response = client.transceiver(_payload)
        if response['status'] != 0:
            complete_task(self.task['job_id'], self.task['task_id'],
                          {'status': 'ERROR', 'response': 'Dispatch Error: %s' % response})
        return response['data']  # This is the actual return information

    @classmethod
    def create(cls):
        # noinspection PyPep8Naming
        return cls(config.rpc.redis.host, config.rpc.redis.port,
                   config.rpc.redis.queue)

def configure_logging():
    logging.basicConfig(level=logging.getLevelName(config.log_level),
                        format=config.log_format)

def main():
    # config is global so that we can use it for Task.create. The threadpool
    # implementation is overkill and was an early design. I will be creating a
    # JIRA to replace worker with a coroutine that can be popped on the frontend
    # event loop
    # - Jared 11/6/2017 (November 6th, 2017, For my non-americans :))

    global config
    config = options()

    configure_logging()

    # Set this up for access from our threads
    RPCCollectionFactory(
        servers=config.rpc.db.servers,
        database=config.rpc.db.name,
        jobs_collection=config.rpc.db.jobs_collection,
        tasks_collection=config.rpc.db.tasks_collection,
        replica_name=config.rpc.db.replica_name
    )

    manager = Manager(RPCTask, config.rpc.worker.threads,
                      config.rpc.worker.max_requests_per_thread)
    manager.manage()


if __name__ == '__main__':
    main()
