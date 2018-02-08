import logging

from mercury.common.asyncio.clients.async_router_req_client import \
    AsyncRouterReqClient

log = logging.getLogger(__name__)


class QueueServiceClient(AsyncRouterReqClient):
    service_name = 'RPC Queue Service'

    async def enqueue_task(self, task):
        """

        :param task:
        :return:
        """
        _payload = {
            'endpoint': 'enqueue_task',
            'args': [task]
        }
        return await self.transceiver(_payload)
