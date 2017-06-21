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

from mercury.common.transport import SimpleRouterReqClient

log = logging.getLogger(__name__)


class BackEndClient(SimpleRouterReqClient):
    _service_name = 'Backend'

    def register(self, device_info, agent_info):
        _payload = {
            'endpoint': 'register',
            'args': [device_info, agent_info]
        }
        return self.transceiver(_payload)

    def update(self, mercury_id, update_data):
        _payload = {
            'endpoint': 'update',
            'args': [mercury_id, update_data]
        }
        return self.transceiver(_payload)

    def task_return(self, return_data):
        _payload = {
            'action': 'task_return',
            'return_data': return_data
        }
        return self.transceiver(_payload)

    def task_update(self, update_data):
        _payload = {
            'action': 'task_update',
            'update_data': update_data
        }
        return self.transceiver(_payload)
