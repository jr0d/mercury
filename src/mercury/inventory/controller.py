import logging

from mercury.inventory.db import InventoryDBController

from mercury.common.asyncio.endpoints import (
    async_endpoint, StaticEndpointController
)
from mercury.common.exceptions import EndpointError
from mercury.common.mongo import (
    serialize_object_id,
    deserialize_object_id
)

log = logging.getLogger(__name__)


class InventoryController(StaticEndpointController):
    """ Inventory controller """
    def __init__(self,
                 inventory_collection):
        """

        :param inventory_collection:
        """
        self.inventory_collection = inventory_collection
        self.db = InventoryDBController(inventory_collection)

        super(InventoryController, self).__init__()

    @async_endpoint('insert_one')
    async def insert_one(self, device_info):
        mercury_id = device_info.get('device_info')
        if not mercury_id:
            EndpointError('device_info packet must contain a mercury_id',
                          'insert_one', device_info)
        return {'object_id': str(await self.db.insert_one(device_info))}

    @async_endpoint('update_one')
    async def update_one(self, mercury_id, update_data):
        if 'mercury_id' in update_data:
            raise EndpointError('Cannot update mercury_id with this method',
                                'update_one', update_data)
        log.debug('Updating {}'.format(mercury_id))
        return {'object_id': serialize_object_id(
            await self.db.update_one(mercury_id, update_data))}

    @async_endpoint('delete')
    async def delete(self, mercury_id):
        return await self.db.delete(mercury_id=mercury_id)

    @async_endpoint('get_one')
    async def get_one(self, mercury_id, projection=None):
        return serialize_object_id(
            await self.db.get_one(mercury_id=mercury_id, projection=projection))

    @async_endpoint('query')
    async def query(self, q, projection, limit=0, sort_direction=1):
        c = self.db.query(query=deserialize_object_id(q),
                          extra_projection=projection,
                          limit=limit,
                          sort_direction=sort_direction)

        total_items = await c.count()

        items = []
        async for document in c:
            items.append(serialize_object_id(document))

        return {
            'total': total_items,
            'limit': limit,
            'items': items,
            'sort_direction': sort_direction > 0 and 'ASCENDING' or 'DESCENDING'
        }

    @async_endpoint('count')
    async def count(self, q):
        return await self.db.count(query=q)
