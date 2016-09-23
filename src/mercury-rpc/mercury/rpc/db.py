# Copyright 2015 Jared Rodriguez (jared.rodriguez@rackspace.com)
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

"""
Document schema:

    mercury_id:
    rpc_address:
    rpc_port:
    ping_address:
    ping_port:
    capabilities: [
        name:
        desc:
        args: int
        kwargs: [key1, key2, keyN]
        usage:
    ]
"""
import logging
import time

log = logging.getLogger(__name__)


class ActiveInventoryDBController(object):
    keys = ['mercury_id',
            'rpc_address',
            'rpc_address6',
            'rpc_port',
            'ping_port',
            'capabilities']

    def __init__(self, collection):
        self.collection = collection
        self.collection.create_index('mercury_id', unique=True)

    @classmethod
    def validate(cls, data):
        for k in cls.keys:
            if k not in data:
                return False
        return True

    @staticmethod
    def data_format(data):
        return 'mercury_id: {mercury_id}, server: {rpc_address}, rpc_port: {rpc_port}, ' \
               'ping_port: {ping_port}'.format(**data)

    def insert(self, data, perform_update=True):
        document = self.get_one(data['mercury_id'])

        data['time_created'] = time.time()

        if document:
            log.warning(
                'Attempted insert of existing object. Offending: %s' % data['mercury_id'])

            if perform_update:
                log.info('Performing insert: %s' % self.data_format(data))
                self.collection.update_one({'mercury_id': data['mercury_id']}, {'$set': data})
            return document['_id']

        log.info(
            'Adding active inventory: %s' % self.data_format(data))
        return self.collection.insert_one(data).inserted_id

    def delete(self, mercury_id):
        log.debug('Deleting mercury_id: %s' % mercury_id)
        document = self.collection.find_one_and_delete({'mercury_id': mercury_id},
                                                       projection=['mercury_id',
                                                                   'time_created'])
        if not document:
            log.info('%s was already removed' % mercury_id)
            return

        now = time.time()
        log.info('Removed mercury_id: %s, lived: %s' % (mercury_id,
                                                        now - document['time_created']))

    def get_one(self, mercury_id, projection=None):
        return self.collection.find_one({'mercury_id': mercury_id}, projection=projection)

    def query(self, query, projection=None):
        if not projection:
            projection = {'mercury_id': 1}
        return self.collection.find(query, projection=projection)

    def exists(self, mercury_id):
        return bool(self.collection.count({'mercury_id': mercury_id}))

