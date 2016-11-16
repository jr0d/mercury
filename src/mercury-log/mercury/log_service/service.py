import time

from mercury.common.transport import SimpleRouterReqService


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
        pass

