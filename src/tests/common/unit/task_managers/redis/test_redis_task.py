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

from mercury.common.task_managers.redis import task
from tests.common.unit.base import MercuryCommonUnitTest


class RedisTaskTest(MercuryCommonUnitTest):
    """Tests for the mercury.common.task_managers.redis.task"""
    @mock.patch('redis.Redis')
    def setUp(self, mock_redis):
        self.redisTask = task.RedisTask(None, None, 'rpc_tasks')

    def test_fetch(self):
        """Test fetch() with JSON data in 'rpc_task' queue"""
        self.redisTask.redis.blpop.return_value = [
            'rpc_tasks',
            '{"task_id": "1", "time_updated": 10}'
        ]

        fetched_task = self.redisTask.fetch()

        self.assertEqual('1', fetched_task['task_id'])
        self.assertEqual(10, fetched_task['time_updated'])

    def test_fetch_empty_redis(self):
        """Test fetch() with an empty 'rpc_task' queue"""
        self.redisTask.redis.blpop.return_value = None

        fetched_task = self.redisTask.fetch()
        self.assertIsNone(fetched_task)

    def test_fetch_not_json(self):
        """Test fetch() with incorrect data in 'rpc_task' queue"""
        self.redisTask.redis.blpop.return_value = [
            'rpc_tasks',
            'fake_data'
        ]

        fetched_task = self.redisTask.fetch()
        self.assertIsNone(fetched_task)
