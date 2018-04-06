import time
import logging

from mercury.common.asyncio.endpoints import async_endpoint, \
    StaticEndpointController
from mercury.common.exceptions import MercuryClientException
from mercury.backend.active_asyncio import active_state, add_active_record

log = logging.getLogger(__name__)


class BackendController(StaticEndpointController):
    agent_info_keys = ['rpc_address',
                       'rpc_address6',
                       'rpc_port',
                       'ping_port',
                       'capabilities']

    @classmethod
    def validate_agent_info(cls, data):
        missing = []
        for k in cls.agent_info_keys:
            if k not in data:
                missing.append(k)

        if missing:
            log.error('Agent info missing: {}'.format(missing))
            return False

        return True

    def __init__(self, service_info, inventory_client, rpc_client):
        """
        Backend controller for servicing agent requests

        :param service_info: RPC Service information to publish
        :param inventory_client: The inventory backend client
        :param jobs_collection: mongodb jobs collection object
        """
        self.service_info = service_info
        self.inventory_client = inventory_client
        self.rpc_client = rpc_client

        super(BackendController, self).__init__()

    @async_endpoint('register')
    async def register(self, device_info, agent_info):
        """
        Registration endpoint for all clients. Everything starts here. This method
        will update the device_info payload to include information about itself as the origin.
        The origin is the associated frontend controller's address and port.

        Note, because we are using ZeroMQ as the transport, we don't have TCP envelope
        information, which means we always need to provide host information above the transport
        layer. This leads to a spoofing vector, as such, the inventory controller will soon
        require that Backends be registered, encrypt their messages, and provide an authentication
        token.

        :param device_info: Device information gathered by agent inspectors
        :param agent_info: Agent transport information
        :return: InventoryController response
        """
        if not self.validate_agent_info(agent_info):
            log.debug('Agent payload: {}'.format(agent_info))
            raise MercuryClientException('Received invalid data from agent')

        agent_info['active_since'] = time.time()
        device_info.update(
            {
                'active': agent_info,
                'origin': self.service_info
            }
        )

        response = await self.inventory_client.insert_one(device_info)
        log.debug(
            'Created/Updated inventory record: %s' %
            response['message']['object_id'])

        add_active_record(device_info)

        return response

    @async_endpoint('update')
    async def update(self, mercury_id, update_data):
        """
        The agents do not have direct access to the Inventory system, as such, we must
        proxy requests for the agent when necessary.

        If the device does not exist in the active_state singleton, an error will be raised

        :param mercury_id:
        :param update_data:
        :return: InventoryController response
        """

        if mercury_id not in active_state:
            raise MercuryClientException(
                'Received update for inactive device: {}'.format(mercury_id))

        log.debug('Received inventory update request for {}'.format(mercury_id))

        return await self.inventory_client.update_one(mercury_id, update_data)

    @async_endpoint('update_task')
    async def update_task(self, update_data):
        """
        Update an agent task that is currently running

        :param update_data: update data containing a task_id
        :return: dict
        """

        log.info('Dispatching task update: {}'.format(update_data))
        return await self.rpc_client.update_task(update_data)

    @async_endpoint('complete_task')
    async def complete_task(self, return_data):
        """
        Complete a task
        :param return_data: the task data containing a job and task id
        :return: dict
        """

        self.validate_required(['status', 'message'],
                               return_data)

        # frontend job client update here
        log.info('Dispatching task complete notification: job_id: {job_id} , '
                 'task_id: {task_id}'.format(**return_data))
        return await self.rpc_client.complete_task(return_data)

