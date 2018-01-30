from mercury.common.clients.router_req_client import RouterReqClient
from mercury.common.asyncio.clients.async_router_req_client import \
    AsyncRouterReqClient


class RPCClient(RouterReqClient):
    service_name = 'RPC Service'

    def update_task(self, update_data):
        """

        :param update_data:
        :return:
        """
        return self.transceiver({
            'endpoint': 'update_task',
            'args': [update_data]
        })

    def complete_task(self, result_data):
        """
        :param result_data:
        :return:
        """
        return self.transceiver({
            'endpoint': 'complete_task',
            'args': [result_data]
        })


class AsyncRPCClient(AsyncRouterReqClient):
    service_name = 'RPC client'

    async def update_task(self, update_data):
        """

        :param update_data:
        :return:
        """
        return await self.transceiver({
            'endpoint': 'update_task',
            'args': [update_data]
        })

    async def complete_task(self, result_data):
        """
        :param result_data:
        :return:
        """
        return await self.transceiver({
            'endpoint': 'complete_task',
            'args': [result_data]
        })
