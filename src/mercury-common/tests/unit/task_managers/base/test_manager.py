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
import threading

from mercury.common.task_managers.base import manager
from mercury.common.task_managers.base import task
from mercury.common.task_managers.base import worker
from tests.unit.base import MercuryCommonUnitTest


class ManagerTest(MercuryCommonUnitTest):
    def setUp(self):
        self.task_handler = task.Task()
        self.fake_manager = manager.Manager(self.task_handler)

    @mock.patch.object(task.Task, 'create')
    @mock.patch.object(threading.Thread, 'start')
    def test_spawn(self, mock_task_create, mock_start):
        """Test that a new worker thread is started by spawn()"""
        self.fake_manager.spawn()
        mock_task_create.assert_called_once()
        mock_start.assert_called_once()
        self.assertEqual(1, len(self.fake_manager.workers))

    @mock.patch.object(task.Task, 'create')
    def set_active_workers(self, mock_task_create):
        """Add two workers to fake_manager"""
        w1 = worker.Worker(self.task_handler, 1, 3600)
        worker_dict1 = {}
        worker_dict1['worker_class'] = w1
        worker_dict1['thread'] = threading.Thread()

        w2 = worker.Worker(self.task_handler, 1, 3600)
        worker_dict2 = {}
        worker_dict2['worker_class'] = w2
        worker_dict2['thread'] = threading.Thread()

        self.fake_manager.workers.append(worker_dict1)
        self.fake_manager.workers.append(worker_dict2)

    @mock.patch.object(manager.Manager, 'active_workers',
                       new_callable=mock.PropertyMock)
    def test_kill_all(self, mock_active):
        """Test that kill_all() switches the kill_signal flag to True for all
        active workers"""
        self.set_active_workers()
        mock_active.return_value = self.fake_manager.workers

        self.fake_manager.kill_all()
        for w in self.fake_manager.workers:
            self.assertTrue(w['worker_class'].kill_signal)

    @mock.patch.object(threading.Thread, "is_alive")
    def test_active_workers_all_active(self, mock_thread):
        """Test active_workers when all workers are active"""
        self.set_active_workers()
        mock_thread.side_effect = [True, True]

        active = self.fake_manager.active_workers
        self.assertEqual(2, len(active))

    @mock.patch.object(threading.Thread, "is_alive")
    def test_active_workers_some_inactive(self, mock_thread):
        """Test active_workers workers when some workers are inactive"""
        self.set_active_workers()
        mock_thread.side_effect = [False, True]

        active = self.fake_manager.active_workers
        self.assertEqual(1, len(active))

    @mock.patch.object(threading.Thread, "is_alive")
    def test_active_workers_all_inactive(self, mock_thread):
        """Test active_workers workers when all workers are inactive"""
        self.set_active_workers()
        mock_thread.side_effect = [False, False]

        active = self.fake_manager.active_workers
        self.assertEqual([], active)
