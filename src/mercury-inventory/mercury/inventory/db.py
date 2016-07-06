# Copyright 2015 Jared Rodriguez (jared at blacknode dot net)
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import logging
import time

from mercury.common.exceptions import MercuryCritical, MercuryGeneralException

log = logging.getLogger(__name__)


class InventoryDBController(object):
    def __init__(self, collection):
        self.collection = collection
        self.collection.create_index('mercury_id', unique=True)

    def insert_one(self, data):
        mercury_id = data.get('mercury_id')
        if not mercury_id:
            raise MercuryCritical('MercuryID is missing from payload. Shame. Shame. Shame.')

        existing = self.collection.find_one({'mercury_id': mercury_id}, projection={'_id': 1})
        if existing:
            # implicit update
            log.info('Record exists, performing update instead.')
            del data['mercury_id']
            self.update_one(mercury_id, data)
            return existing['_id']

        now = time.time()
        data['time_created'] = now
        data['time_updated'] = now

        insert_result = self.collection.insert_one(data)
        return insert_result.inserted_id

    def update_one(self, mercury_id, data=None):
        """
        Very simple update_one/insert method. Here monitor hooks will be run.

        Monitor hooks will inspect the update data for information they care about and perform
        some sort of action. For instance, one such hook may monitor for an update containing
        LLDP information. The hook might publish this transaction to a subscriber interested in
        such things.

        TODO: change function name to update_one.
        TODO: update prototype so that it takes the arguments, mercury_id, data=None
            (if data is None, create an empty dict and touch time_updated)
        :param mercury_id: The update target
        :param data: The update or insert data
        :return:
        """
        data = data or {}

        if not data:
            log.warning('Update data is empty')

        if not self.collection.count({'mercury_id': mercury_id}, projection={'_id': 1}):
            raise MercuryGeneralException('Attempting to update non-existing record')

        if 'mercury_id' in data:
            raise MercuryCritical('MercuryID cannot be updated once a record already exists')

        data['time_updated'] = time.time()
        self.collection.update_one({'mercury_id': mercury_id}, {'$set': data})

    def delete(self, mercury_id):
        log.info('Deleting: %s' % mercury_id)
        self.collection.delete_one({'mercury_id': mercury_id})

    def get_one(self, mercury_id, projection=None):
        log.debug('Fetching: %s' % mercury_id)
        return self.collection.find_one({'mercury_id': mercury_id}, projection=projection)

    def query(self, query, extra_projection=None):
        log.debug('Executing query: %s' % query)
        projection = {'mercury_id': 1}
        if extra_projection:
            projection.update(extra_projection)
        return self.collection.find(query, projection=projection)
