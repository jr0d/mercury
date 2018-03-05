import logging
import time

from mercury.common.exceptions import MercuryCritical, MercuryGeneralException

from mercury.inventory.hooks import get_hooks_from_data, run_hooks

log = logging.getLogger(__name__)


class InventoryDBController(object):
    def __init__(self, collection):
        self.collection = collection
        self.collection.create_index('mercury_id', unique=True)

    async def insert_one(self, data):
        mercury_id = data.get('mercury_id')
        if not mercury_id:
            raise MercuryCritical(
                'MercuryID is missing from payload. Shame. Shame. Shame.')

        existing = await self.collection.find_one({'mercury_id': mercury_id},
                                                  projection={'_id': 1})
        if existing:
            # implicit update
            log.info('Record exists, performing update instead.')
            del data['mercury_id']
            await self.update_one(mercury_id, data)
            return existing['_id']

        now = time.time()
        data['time_created'] = now
        data['time_updated'] = now

        insert_result = await self.collection.insert_one(data)
        return insert_result.inserted_id

    async def update_one(self, mercury_id, data=None):
        """
        Very simple update_one/insert method. Here monitor hooks will be run.

        Monitor hooks will inspect the update data for information they care about and perform
        some sort of action. For instance, one such hook may monitor for an update containing
        LLDP information. The hook might publish this transaction to a subscriber interested in
        such things.

        :param mercury_id: The update target
        :param data: The update or insert data
        :return:
        """
        data = data or {}
        upsert = False

        if not data:
            log.warning('Update data is empty')

        if not await self.collection.count({'mercury_id': mercury_id},
                                           projection={'_id': 1}):
            raise MercuryGeneralException(
                'Attempting to update non-existing record')

        if 'mercury_id' in data:
            raise MercuryCritical(
                'MercuryID cannot be updated once a record already exists')

        hooks = get_hooks_from_data(data)
        if hooks:
            # We care about how this data is handled
            upsert = True
            run_hooks(hooks, data)

        data['time_updated'] = time.time()
        await self.collection.update_one({'mercury_id': mercury_id},
                                         {'$set': data}, upsert=upsert)

    async def delete(self, mercury_id):
        log.info('Deleting: %s' % mercury_id)
        await self.collection.delete_one({'mercury_id': mercury_id})

    def get_one(self, mercury_id, projection=None):
        log.debug('Fetching: %s' % mercury_id)
        return self.collection.find_one({'mercury_id': mercury_id},
                                        projection=projection)

    # TODO: Ditch query and add find() and find_one()
    def query(self, query, extra_projection=None, limit=0, sort='_id',
              sort_direction=1):
        log.debug(
            'Executing query: {} limit: {} key: {} direction: {}'.format(query,
                                                                         limit,
                                                                         sort,
                                                                         sort_direction))

        projection = {'mercury_id': 1}

        if extra_projection:
            projection.update(extra_projection)

        c = self.collection.find(query, projection=projection)

        if limit:
            c.limit(limit)

        if sort:
            c.sort(sort, sort_direction)

        return c

    def count(self, query):
        return self.collection.count(query)
