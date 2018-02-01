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

"""Generic mongodb facilities"""

import bson
import logging
import pymongo


log = logging.getLogger(__name__)


def get_connection(server_or_servers=None, replica_set=None,
                   username=None, password=None):
    """Creates a new MongoDB client.

    :param server_or_servers: Hostname / MongoDB URI or list of hostnames /
        URIs for the client to connect to.
    :param replica_set: The name of the replica set to connect to.
    :param username:
    :param password:
    :returns: A MongoClient instance.
    """
    servers = server_or_servers
    if servers is not None:
        if not isinstance(servers, list):
            servers = [servers]

    log.info('Connecting to %s : replicaSet: %s' % (servers, replica_set))

    if username:
        return pymongo.MongoClient(servers, replicaset=replica_set,
                                   username=username, password=password)
    else:
        return pymongo.MongoClient(servers, replicaset=replica_set)


class MongoCollection(object):
    def __init__(self,
                 database,
                 collection,
                 server_or_servers=None,
                 replica_set=None):
        """Get a collection from a Mongo database.

        :param database: The name of the database containing the collection.
        :param collection: The name of the collection.
        :param server_or_servers: Hostname / MongoDB URI or list of hostnames /
            URIs for the client to connect to.
        :param replica_set: The name of the replica set to connect to.
        :raises: InvalidName if the database or collection name is invalid.
        """
        self.servers = server_or_servers
        self.replica_set = replica_set
        self.database_name = database
        self.collection_name = collection

        self.connection = get_connection(self.servers, self.replica_set)

        log.debug('database: %s' % self.database_name)
        self.db = self.connection[self.database_name]
        log.debug('collection: %s' % self.collection_name)
        self.collection = self.db[self.collection_name]


def get_collection(database,
                   collection,
                   connection=None,
                   server_or_servers=None,
                   replica_set=None):
    """Get a collection from a Mongo database.

    :param database: The name of the database containing the collection.
    :param collection: The name of the collection.
    :param connection: A MongoClient instance.
    :param server_or_servers: Hostname / MongoDB URI or list of hostnames /
        URIs for the client to connect to.
    :param replica_set: The name of the replica set to connect to.
    :returns: A MongoDB collection.
    :raises: InvalidName if the database or collection name is invalid.
    """
    database_name = database
    collection_name = collection

    if not connection:
        connection = get_connection(server_or_servers, replica_set)

    log.info('database: %s' % database_name)
    db = connection[database_name]
    log.info('collection: %s' % collection_name)
    return db[collection_name]


def serialize_object_id(obj):
    if isinstance(obj, bson.ObjectId):
        obj = str(obj)

    if isinstance(obj, dict):
        if '_id' in obj:
            obj['_id'] = str(obj['_id'])
    return obj


def deserialize_object_id(obj):
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
