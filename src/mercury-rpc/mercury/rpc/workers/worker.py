import logging


from mercury.common.task_managers.base.manager import Manager
from mercury.common.task_managers.redis.task import RedisTask
from mercury.common.transport import SimpleRouterReqClient
from mercury.rpc.jobs import update_task

log = logging.getLogger(__name__)


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
            update_task(self.task['task_id'],
                       {'status': 'ERROR', 'response': 'Dispatch Error: %s' % response})
        return response

    @classmethod
    def create(cls):
        # TODO: create should read this information from the configuration
        # noinspection PyPep8Naming
        RPC_QUEUE = 'rpc_tasks'
        return cls(RPC_QUEUE)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    manager = Manager(RPCTask, 10, 3600)
    manager.manage()
