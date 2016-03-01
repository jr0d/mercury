# Copyright 2015 Jared Rodriguez (jared at blacknode dot net)
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
    def register(self, client_info):
        _payload = {
            'action': 'register',
            'client_info': client_info
        }
        return self.transceiver(_payload)

    def push_response(self, response_data):
        _payload = {
            'action': 'task_return',
            'response': response_data
        }
        return self.transceiver(_payload)
