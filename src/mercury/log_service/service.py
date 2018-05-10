import logging
import time

from mercury.common.configuration import MercuryConfiguration
from mercury.common.exceptions import MercuryClientException
from mercury.common.mongo import get_collection, get_connection
from mercury.common.transport import SimpleRouterReqService

LOG = logging.getLogger(__name__)

MERCURY_LOG_CONFIG = 'mercury-log.yaml'


def options():
    configuration = MercuryConfiguration(
        'mercury-log',
        MERCURY_LOG_CONFIG,
        description='The mercury logging backend')

    configuration.add_option('log_service.bind_address',
                             default='tcp://127.0.0.1:9006',
                             help_string='The address to bind to'
                             )

    configuration.add_option('log_service.db.servers',
                             default='127.0.0.1:27017',
                             special_type=list,
                             help_string='Server or coma separated list of '
                                         'servers to connect to')

    configuration.add_option('log_service.db.name',
                             config_address='log_service.db.name',
                             default='test',
                             help_string='The database for our collections')

    configuration.add_option('log_service.db.collection',
                             default='log',
                             help_string='The collection for our documents')

    configuration.add_option('log_service.db.replica_name',
                             help_string='An optional replica')

    return configuration.scan_options()


class AgentLogService(SimpleRouterReqService):
    """
    Logging aggregation end point for MercuryAgents
    """

    def __init__(self, bind_address, log_collection):
        super(AgentLogService, self).__init__(bind_address)
        self.log_collection = log_collection

    @staticmethod
    def validate_message(message):
        LOG.debug(message)
        required = [
            'levelno',
            'pathname',
            'message',
            'name'
        ]

        for req in required:
            if req not in message:
                return False

        return True

    @staticmethod
    def set_job_info_from_thread(message):
        """
        The task runner thread (agent.task_runner) has the following naming
        convention:

        _<job_id>_<task_id>

        This lets us associate logging messages to jobs/tasks from within the
        execution thread.
        :param message: reference to the log message
        :return: None
        """
        thread_name = message.get('threadName')
        if thread_name and thread_name[0] == '_':
            job_id, task_id = thread_name.split('_')[1:]
            message['job_id'] = job_id
            message['task_id'] = task_id

    def process(self, message):
        if not self.validate_message(message):
            raise MercuryClientException('Invalid message')

        message.update({'time_created': time.time()})

        self.set_job_info_from_thread(message)

        self.log_collection.insert(message)

        return {'message': 'ok', 'error': False}


def main():
    config = options()
    logging.basicConfig(level=logging.getLevelName(config.logging.level),
                        format=config.logging.format)

    db_connection = get_connection(config.log_service.db.servers,
                                   config.log_service.db.replica_name)

    collection = get_collection(config.log_service.db.name,
                                config.log_service.db.collection,
                                db_connection)

    agent_log_service = AgentLogService(config.log_service.bind_address,
                                        collection)

    LOG.info('Starting logging backend on {}'.format(
        config.log_service.bind_address))

    agent_log_service.start()


if __name__ == '__main__':
    main()
