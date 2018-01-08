import logging

from mercury.common.transport import SimpleRouterReqClient

log = logging.getLogger(__name__)


class QueueServiceClient(SimpleRouterReqClient):
    service_name = 'RPC Queue Service'

    def enqueue_task(self, task):
        """

        :param task:
        :return:
        """
        _payload = {
            'endpoint': 'enqueue_task',
            'args': [task]
        }
        return self.transceiver(_payload)
