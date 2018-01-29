# Copyright 2017 Jared Rodriguez (jared.rodriguez@rackspace.com)
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

from mercury.common.clients.router_req_client import RouterReqClient


log = logging.getLogger(__name__)


class RPCFrontEndClient(RouterReqClient):
    """Client for RPC Front End"""

    service_name = 'RPC frontend'

    def get_job(self, job_id, projection=None):
        """

        :param job_id:
        :param projection:
        :return:
        """
        payload = {
            'endpoint': 'get_job',
            'args': [job_id],
            'kwargs': {
                'projection': projection
            }
        }
        return self.transceiver(payload)

    def get_job_status(self, job_id):
        """

        :param job_id:
        :return:
        """
        payload = {
            'endpoint': 'get_job_status',
            'args': [job_id]
        }
        return self.transceiver(payload)

    def get_job_tasks(self, job_id, projection=None):
        """

        :param job_id:
        :param projection:
        :return:
        """
        payload = {
            'endpoint': 'get_job_tasks',
            'args': [job_id],
            'kwargs': {
                'projection': projection
            }
        }

        return self.transceiver(payload)

    def get_task(self, task_id):
        """

        :param task_id:
        :return:
        """
        payload = {
            'endpoint': 'get_task',
            'args': [task_id]
        }
        return self.transceiver(payload)

    def get_jobs(self, projection=None):
        """

        :param projection:
        :return:
        """
        payload = {
            'endpoint': 'get_jobs',
            'kwargs': {
                'projection': projection
            }
        }
        return self.transceiver(payload)

    def create_job(self, query, instruction):
        """

        :param query:
        :param instruction:
        :return:
        """
        payload = {
            'endpoint': 'create_job',
            'args': [query, instruction]
        }
        log.debug('Dispatching query {query} : {instruction}')
        return self.transceiver(payload)
