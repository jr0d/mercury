import json
import logging
import redis

from mercury.common.exceptions import MercuryClientException
from mercury.common.transport import SimpleRouterReqService

from mercury.backend.queue_service.options import parse_options

log = logging.getLogger(__name__)


class QueueService(SimpleRouterReqService):
    """ Simple backend for queuing tasks """

    REQUIRED_TASK_KEYS = ['host', 'port', 'task_id', 'job_id', 'method', 'args',
                          'kwargs']

    def __init__(self, bind_address, redis_client, queue_name):
        """

        :param bind_address:
        :param redis_client:
        :param queue_name:
        """
        super(QueueService, self).__init__(bind_address)
        self.redis_client = redis_client
        self.queue_name = queue_name

    def enqueue_task(self, task):
        """

        :param task:
        :return:
        """
        self.validate_required(self.REQUIRED_TASK_KEYS, task)

        log.debug('Enqueuing task: {job_id} / {task_id}'.format(**task))

        self.redis_client.lpush(self.queue_name, json.dumps(task))

    def process(self, message):
        """

        :param message:
        :return:
        """
        if message['endpoint'] != 'enqueue_task':
            raise MercuryClientException('Unsupported endpoint')

        self.enqueue_task(message['args'][0])

        return dict(error=False, message='Done')


def configure_logging(config):
    """ Configure logging for application
    :param config: A namespace provided from MercuryConfiguration.parse_args
    """
    logging.basicConfig(level=logging.getLevelName(config.logging.level),
                        format=config.logging.format)


def main():
    """ Service entry point """
    config = parse_options()

    configure_logging(config)

    redis_client = redis.Redis(host=config.backend.redis.host,
                               port=config.backend.redis.port)

    server = QueueService(config.backend.queue_service.bind_address,
                          redis_client,
                          config.backend.redis.queue)
    server.start()


if __name__ == '__main__':
    main()
