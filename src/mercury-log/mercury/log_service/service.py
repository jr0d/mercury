import logging
import time

from mercury.common.configuration import get_configuration
from mercury.common.exceptions import MercuryGeneralException
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
        required = [
                'mercury_id',
                'level',
                'scope',
                'message',
                'name'
            ]

        for req in required:
            if req not in message:
                return False

        return True

    def process(self, message):
        if not self.validate_message(message):
            raise MercuryGeneralException('Logging controller recieved invalid message')

        message.update({'time_created': time.time()})
        self.log_collection.insert(message)


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
