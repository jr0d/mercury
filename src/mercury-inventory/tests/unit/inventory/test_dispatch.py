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

import mercury.inventory.controller as controller
import mock

from ..base import MercuryInventoryUnitTest


class MercuryDispatcherUnitTest(MercuryInventoryUnitTest):
    # noinspection PyMethodOverriding
    @mock.patch('mercury.inventory.controller.InventoryController')
    def setUp(self, ic_mock):
        super(MercuryDispatcherUnitTest, self).setUp()
        self.dispatcher = dispatch.Dispatcher()

    def test_dispatch_no_endpoint(self):
        fake_message = {
            'args': ['some', 'argument', 'list'],
            'kwargs': {'key': 'word'}
        }

        result = self.dispatcher.dispatch(fake_message)
        # Make sure it popped an error and set a message.
        assert 'error' in result and result['error']
        assert result['message']
