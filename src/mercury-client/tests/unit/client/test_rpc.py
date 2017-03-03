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
"""Module to unit test mercury.client.base"""

import mock

import mercury.client.rpc as client_rpc
from ..base import MercuryClientUnitTest


class TestClientRPC(MercuryClientUnitTest):
    def setUp(self):
        super(TestClientRPC, self).setUp()
        self.target = 'test_target'
        self.JobQuery = client_rpc.JobQuery(
            self.target, 'some_query', 'some_instructions')

    def test_jobs_base_uri(self):
        assert self.JobQuery.SERVICE_URI == 'api/rpc/jobs'

    def test_task_uri(self):
        task_interface = client_rpc.TaskInterface(self.target)
        assert task_interface.SERVICE_URI == 'api/rpc/tasks'

    def test_active_computers_uri(self):
        active_computers = client_rpc.ActiveComputers(self.target)
        assert active_computers.SERVICE_URI == 'api/active/computers'

    def test_post_job(self):
        job_query = client_rpc.JobQuery(
            self.target, 'some_query', 'some_instruction')
        job_query.post = mock.Mock(return_value={'job_id': 'some_id'})
        job_query.post_job()

        job_query.post.assert_called_with(data=
                                          {'query': 'some_query', 'instruction': 'some_instruction'})
        assert job_query.job_id == 'some_id'
