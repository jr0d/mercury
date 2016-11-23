import logging

from mercury.common.exceptions import MercuryGeneralException
from mercury.common.transport import SimpleRouterReqClient

LOG = logging.getLogger('')


class MercuryLogHandler(logging.Handler):
    def __init__(self, service_url, mercury_id=None):
        super(MercuryLogHandler, self).__init__()

        self.service_url = service_url
        self.__mercury_id = mercury_id

        self.client = SimpleRouterReqClient(self.service_url)

    def emit(self, record):
        if not self.__mercury_id:
            return

        data = record.__dict__
        data.update({'mercury_id': self.__mercury_id})

        response = self.client.transceiver(data)
        if not response:
            raise MercuryGeneralException('Did not receive response from server')

    def set_mercury_id(self, mercury_id):
        self.__mercury_id = mercury_id
