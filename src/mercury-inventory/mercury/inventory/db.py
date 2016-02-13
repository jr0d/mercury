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


log = logging.getLogger(__name__)

__scaffold = {
    'mercury_id': '',
    'interfaces': [],
    'pci': [],
    'processors': {},
    'memory_modules': [],
    'os_storage': [],
    'raid': {},
    'dmi': {},
    'efi': {},
    'obm': {},
    'dhcp_info': {}
}


class InventoryDBController(object):
    def __init__(self, collection):
        self.collection = collection
        self.collection.ensure_index('mercury_id', unique=True)

    def update(self, data):
        mercury_id = data.get('mercury_id')
        if not mercury_id:
            raise Exception('MercuryID is missing from data')

        existing = self.collection.find_one({'mercury_id': mercury_id}, projection={'_id': 1})
        if existing:
            object_id = existing['_id']
            data['time_updated'] = time.time()
            log.debug('Updating _id: %s,  m_id: %s' % (object_id, mercury_id))
            self.collection.update_one({'_id': object_id}, {'$set': data})
        else:
            now = time.time()
            data['time_created'] = now
            data['time_updated'] = now
            insert_result = self.collection.insert_one(data)
            object_id = insert_result.inserted_id
            log.info('Created record for %s <ObjectID: %s>' % (mercury_id, object_id))

        return object_id

    def delete(self, mercury_id):
        log.info('Deleting: %s' % mercury_id)
        self.collection.delete_one({'mercury_id': mercury_id})

    def get_one(self, mercury_id):
        log.debug('Fetching: %s' % mercury_id)
        return self.collection.find_one({'mercury_id': mercury_id})

    def query(self, query):
        log.debug('Executing query: %s' % query)
        return self.collection.find(query, projection={'mercury_id': 1})

if __name__ == '__main__':
    from mercury.common.mongo import get_collection
    logging.basicConfig(level=logging.DEBUG)
    c = get_collection('test', 'mercury_inventory')
    idbc = InventoryDBController(c)
    oid = idbc.update({'mercury_id': '12345', 'blah': True})
    log.info('Created : %s' % oid)

    log.info('Get result for 12345: %s' % idbc.get_one('12345'))
    log.info('Get result for x: %s' % idbc.get_one('x'))
    log.info('result: ' + str(list(idbc.query({'blah': True}))))

    idbc.delete('12345')
