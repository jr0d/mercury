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

import logging
import pymongo


log = logging.getLogger(__name__)


def get_connection(server_or_servers=None, replica_set=None):
    servers = server_or_servers
    if servers is not None:
        if not isinstance(servers, list):
            servers = [servers]

    log.info('Connecting to %s : replicaSet: %s' % (servers, replica_set))
    return pymongo.MongoClient(servers, replicaset=replica_set)


class MongoCollection(object):
    def __init__(self,
                 database,
                 collection,
                 server_or_servers=None,
                 replica_set=None):

        self.servers = server_or_servers
        self.replica_set = replica_set
        self.database_name = database
        self.collection_name = collection

        self.connection = get_connection(self.servers, self.replica_set)

        log.debug('database: %s' % self.database_name)
        self.db = self.connection[self.database_name]
        log.debug('collection: %s' % self.collection_name)
        self.collection = self.db[self.collection_name]


def get_collection(database, collection, connection=None, server_or_servers=None, replica_set=None):
        database_name = database
        collection_name = collection

        if not connection:
            connection = get_connection(server_or_servers, replica_set)

        log.info('database: %s' % database_name)
        db = connection[database_name]
        log.info('collection: %s' % collection_name)
        return db[collection_name]
