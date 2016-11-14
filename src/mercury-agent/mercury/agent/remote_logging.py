import logging

from mercury.common.exceptions import MercuryGeneralException
from mercury.common.transport import SimpleRouterReqClient

LOG = logging.getLogger(__name__)


class MercuryLogHandler(logging.Handler):
    def __init__(self, service_url, mercury_id):
        super(MercuryLogHandler, self).__init__()

        self.service_url = service_url
        self.mercury_id = mercury_id

        self.client = SimpleRouterReqClient(self.service_url)

    def emit(self, record):
        data = record.__dict__
        data.update({'mercury_id': self.mercury_id})

        response = self.client.transceiver(data)
        if not response:
            raise MercuryGeneralException('Did not receive response from server')
