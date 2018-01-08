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

from mercury.common.task_managers.base import task
from mercury.common.task_managers.base import worker
from tests.common.unit.base import MercuryCommonUnitTest


class WorkerTest(MercuryCommonUnitTest):
    """Tests for the mercury.common.task_managers.base.worker"""
    @mock.patch.object(task, 'Task')
    def setUp(self, mock_task):
        """Create a fake worker object"""
        mock_task.create.return_value = None

        task_handler = task.Task()
        max_requests = 1
        max_age = 3600
        self.fake_worker = worker.Worker(task_handler, max_requests, max_age,
                                         (), {})

    def test_start(self):
        """Test start() executes a new task"""
        self.fake_worker.start()
        self.fake_worker.task.fetch.assert_called_once()
        self.fake_worker.task.execute.assert_called_once()
        self.assertEqual(1, self.fake_worker.handled_tasks)

    def test_start_kill_signal(self):
        """Test start() doesn't execute task if kill_signal is True"""
        self.fake_worker.kill_signal = True
        self.fake_worker.start()
        self.fake_worker.task.fetch.assert_not_called()
        self.fake_worker.task.execute.assert_not_called()
        self.assertEqual(0, self.fake_worker.handled_tasks)

    def test_start_too_many_requests(self):
        """Test start() doesn't execute more tasks than maximum allowed"""
        self.fake_worker.handled_tasks = 1
        self.fake_worker.start()
        self.fake_worker.task.fetch.assert_not_called()
        self.fake_worker.task.execute.assert_not_called()
        self.assertEqual(1, self.fake_worker.handled_tasks)

    def test_start_no_more_task(self):
        """Test start() continue fetching tasks if none found at first"""
        self.fake_worker.task.fetch.side_effect = [None, 'fake_task']
        self.fake_worker.start()
        self.assertEqual(2, self.fake_worker.task.fetch.call_count)
        self.fake_worker.task.execute.assert_called_once()
        self.assertEqual(1, self.fake_worker.handled_tasks)
