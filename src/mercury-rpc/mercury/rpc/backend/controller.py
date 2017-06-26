import logging

from mercury.common.asyncio.endpoints import async_endpoint, StaticEndpointController
from mercury.common.exceptions import EndpointError
from mercury.rpc.active_asyncio import add_record

log = logging.getLogger(__name__)


class BackendController(StaticEndpointController):
    agent_info_keys = ['mercury_id',
                       'rpc_address',
                       'rpc_address6',
                       'rpc_port',
                       'ping_port',
                       'capabilities']

    @classmethod
    def validate_agent_info(cls, data):
        for k in cls.agent_info_keys:
            if k not in data:
                return False
        return True

    def __init__(self, service_info, inventory_client, jobs_collection, tasks_collection):
        """
        Backend controller for servicing agent requests

        :param service_info: RPC Service information to publish
        :param inventory_client: The inventory service client
        :param jobs_collection: mongodb jobs collection object
        :param tasks_collection: mongodb tasks collection object
        """
        self.service_info = service_info
        self.inventory_client = inventory_client
        self.jobs_collection = jobs_collection
        self.tasks_collection = tasks_collection

        super(StaticEndpointController, self).__init__()

    @async_endpoint('register')
    async def register(self, device_info, agent_info):
        if not self.validate_agent_info(agent_info):
            raise EndpointError('Recieved invalid data from agent', 'register', agent_info)

        device_info.update(
            {
                'active': agent_info,
                'origin': self.service_info
            }
        )

        response = await self.inventory_client.insert_one(device_info)
        log.debug('Created/Updated inventory record: %s' % object_id)

        add_record(agent_info)

        return response

    @async_endpoint('update')
    async def update(self, mercury_id, update_data):
        return await self.inventory_client.update_one(mercury_id, update_data)

