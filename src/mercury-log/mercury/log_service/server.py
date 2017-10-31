import logging
import time

from mercury.common.configuration import get_configuration
from mercury.common.exceptions import MercuryClientException
from mercury.common.mongo import get_collection, get_connection
from mercury.common.transport import SimpleRouterReqService


LOG = logging.getLogger(__name__)


__defaults = {
    'configuration_file': 'mercury-log.yaml'
}


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
                'level',
                'scope',
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
        The task runner thread (agent.task_runner) has the following naming convention:

        _<job_id>_<task_id>

        This lets us associate logging messages to jobs/tasks from within the execution thread.
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
        LOG.debug(message)
        self.log_collection.insert(message)
        return {'message': 'ok'}


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s : %(levelname)s - %(name)s - %(message)s')

    configuration = get_configuration(__defaults['configuration_file'])

    db_connection = get_connection(configuration['db']['servers'],
                                   replica_set=configuration['db']['replica_set'])
    _log_collection = get_collection(configuration['db']['database'],
                                     configuration['db']['collection'],
                                     db_connection)

    _bind_address = configuration['service']['url']

    agent_log_service = AgentLogService(_bind_address, _log_collection)

    LOG.info('Starting logging service on {}'.format(_bind_address))
    agent_log_service.start()
