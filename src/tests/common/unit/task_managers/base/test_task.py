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
from tests.common.unit.base import MercuryCommonUnitTest


class TaskTest(MercuryCommonUnitTest):
    """Tests for the mercury.common.task_managers.base.task"""
    def setUp(self):
        """Create a fake Task object"""
        self.task = task.Task()
        pass

    @mock.patch.object(task.Task, 'do')
    def test_execute(self, mock_do):
        """Test execute() calls do() and reset the task to None"""
        self.task.task = 'fake_task'

        self.task.execute()
        mock_do.assert_called_once()
        self.assertIsNone(self.task.task)

    def test_execute_no_task(self):
        """Test execute() fails when no task is defined"""
        self.assertRaises(Exception, self.task.execute)
