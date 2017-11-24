# Copyright 2017 Rackspace
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

import mock
import pymongo
import pytest

from mercury.common import mongo
from tests.common.unit.base import MercuryCommonUnitTest


@mock.patch('pymongo.MongoClient')
def test_get_connection(mock_mongo_client):
    """Test get_connection() creates a new MongoClient."""
    mongo.get_connection('host1')
    mock_mongo_client.assert_called_with(['host1'], replicaset=None)

    mongo.get_connection(['host1', 'host2'], replica_set='replica_set_name')
    mock_mongo_client.assert_called_with(['host1', 'host2'],
                                         replicaset='replica_set_name')


class MongoCollectionUnitTest(MercuryCommonUnitTest):
    def test___init__(self):
        """Test creation of MongoCollection."""
        collection = mongo.MongoCollection('db_name', 'collection_name')

        assert isinstance(collection.db, pymongo.database.Database)
        assert collection.db.name == 'db_name'
        assert isinstance(collection.collection, pymongo.collection.Collection)
        assert collection.collection.full_name == 'db_name.collection_name'

    def test___init__invalid_names(self):
        """Test creation of MongoCollection with invalid names."""
        with pytest.raises(pymongo.errors.InvalidName) as exc:
            collection = mongo.MongoCollection('', 'collection_name')

        with pytest.raises(pymongo.errors.InvalidName):
            collection = mongo.MongoCollection('db_name', '')


def test_get_collection():
    """Test get_collection()"""
    collection = mongo.get_collection('db_name', 'collection_name')

    assert isinstance(collection, pymongo.collection.Collection)
    assert collection.full_name == 'db_name.collection_name'


def test_get_collection_invalid_names():
    """Test get_collection() with invalid names."""
    with pytest.raises(pymongo.errors.InvalidName):
        collection = mongo.get_collection('', 'collection_name')

    with pytest.raises(pymongo.errors.InvalidName):
        collection = mongo.get_collection('db_name', '')
