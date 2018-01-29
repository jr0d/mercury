import logging

from mercury.common.clients.router_req_client import RouterReqClient

log = logging.getLogger(__name__)


class QueueServiceClient(RouterReqClient):
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
