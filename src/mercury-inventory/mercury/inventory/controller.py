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

import bson
import logging

from mercury.common.mongo import get_collection
from mercury.inventory.db import InventoryDBController
from mercury.inventory.configuration import inventory_configuration
from mercury.inventory.exceptions import EndpointError


LOG = logging.getLogger(__name__)

runtime_endpoints = {}

__all__ = ['InventoryController']


def endpoint(name):
    def wrap(f):
        def wrapped_f(self, *args, **kwargs):
            return f(self, *args, **kwargs)

        LOG.debug('Adding runtime endpoint %s (%s)' % (f.__name__, name))
        runtime_endpoints[name] = f
        wrapped_f.__name__ = f.__name__
        wrapped_f.__doc__ = f.__doc__
        return wrapped_f
    return wrap


class InventoryController(object):
    def __init__(self):
        self.db_configuration = inventory_configuration.get('inventory', {}).get('db', {})
        LOG.debug('DB Configuration: %s' % self.db_configuration)

        db_name = self.db_configuration.get('name')
        if not db_name:
            LOG.warning('DB name is not specified, using test')
            db_name = 'test'

        self.collection = get_collection(
            db_name,  # Perhaps we should raise an exception
            self.db_configuration.get('collection', 'inventory'),
            server_or_servers=self.db_configuration.get('servers', ['localhost']),
            replica_set=self.db_configuration.get('replica_set')
        )
        self.db = InventoryDBController(self.collection)
        self.endpoints = runtime_endpoints

    @staticmethod
    def __serialize_object_id(obj):
        if isinstance(obj, bson.ObjectId):
            obj = str(obj)

        if isinstance(obj, dict):
            if '_id' in obj:
                obj['_id'] = str(obj['_id'])
        return obj

    @staticmethod
    def __deserialize_object_id(obj):
        if '_id' in obj:
            if isinstance(obj['_id'], dict):
                # ex: {'_id': {'$gt': 'xxxxx'}}
                for key, value in list(obj['_id'].items()):
                    if bson.ObjectId.is_valid(value):
                        obj['_id'][key] = bson.ObjectId(value)
                        break  # there should only be one
            elif isinstance(obj['_id'], str):
                obj['_id'] = bson.ObjectId(obj['_id'])
        return obj

    @endpoint('index')
    def index(self):
        return 'Hello World'

    @endpoint('insert_one')
    def insert_one(self, device_info):
        mercury_id = device_info.get('device_info')
        if not mercury_id:
            EndpointError('device_info packet must contain a mercury_id', 'insert_one', device_info)
        return {'object_id': str(self.db.insert_one(device_info))}

    @endpoint('update_one')
    def update_one(self, mercury_id, update_data):
        if 'mercury_id' in update_data:
            raise EndpointError('Cannot update mercury_id with this method', 'update_one', update_data)
        return {'object_id': self.__serialize_object_id(self.db.update_one(mercury_id, update_data))}

    @endpoint('delete')
    def delete(self, mercury_id):
        return self.db.delete(mercury_id=mercury_id)

    @endpoint('get_one')
    def get_one(self, mercury_id, projection=None):
        return self.__serialize_object_id(self.db.get_one(mercury_id=mercury_id, projection=projection))

    @endpoint('query')
    def query(self, q, projection, limit=0, sort_direction=1):
        c = self.db.query(query=self.__deserialize_object_id(q),
                          extra_projection=projection,
                          limit=limit,
                          sort_direction=sort_direction)

        total_items = c.count()  # I am not sure if counting twice is worth it

        items = []
        for document in c:
            items.append(self.__serialize_object_id(document))

        return {
            'total': total_items,
            'limit': limit,
            'items': items,
            'direction': sort_direction > 0 and 'ASCENDING' or 'DESCENDING'
        }

    @endpoint('count')
    def count(self, q):
        return self.db.count(query=q)
