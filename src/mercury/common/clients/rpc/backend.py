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

from mercury.common.clients.router_req_client import RouterReqClient

log = logging.getLogger(__name__)


class BackEndClient(RouterReqClient):
    service_name = 'RPC backend'

    def register(self, device_info, agent_info):
        """

        :param device_info:
        :param agent_info:
        :return:
        """
        _payload = {
            'endpoint': 'register',
            'args': [device_info, agent_info]
        }
        return self.transceiver(_payload)

    def update(self, mercury_id, update_data):
        """

        :param mercury_id:
        :param update_data:
        :return:
        """
        _payload = {
            'endpoint': 'update',
            'args': [mercury_id, update_data]
        }
        return self.transceiver(_payload)

    def complete_task(self, return_data):
        """
        :param return_data:
        :return:
        """
        _payload = {
            'endpoint': 'complete_task',
            'args': [return_data]
        }
        return self.transceiver(_payload)

    def update_task(self, update_data):
        """
        :param update_data:
        :return:
        """
        _payload = {
            'endpoint': 'update_task',
            'args': [update_data]
        }
        return self.transceiver(_payload)
