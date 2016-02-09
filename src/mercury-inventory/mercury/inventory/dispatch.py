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
import sys
import traceback

from mercury.inventory.controller import InventoryController
from mercury.inventory.exceptions import EndpointError

LOG = logging.getLogger(__name__)


class Dispatcher(object):
    def __init__(self):
        self.ic = InventoryController()

    def dispatch(self, message):
        endpoint = message.get('endpoint')
        args = message.get('args', [])
        kwargs = message.get('kwargs', {})

        if not endpoint:
            LOG.debug('Recieved message with no endpoint')
            return dict(error=True, message='Endpoint not specified in message')

        if endpoint not in self.ic.endpoints:
            LOG.debug('Received request to unsupported endpoint: %s' % endpoint)
            return dict(error=True, message='Endpoint is not supported')

        try:
            response = self.ic.endpoints[endpoint](self.ic, *args, **kwargs)
        except EndpointError as endpoint_error:
            tb = traceback.format_exception(*sys.exc_info())
            LOG.error('Endpoint Error: endpoint=%s, message=%s, traceback=%s' % (
                endpoint,
                endpoint_error.message,
                '\n'.join(tb)
            ))
            return dict(error=True, traceback=tb, message=endpoint_error.message)

        return dict(error=False, response=response)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    d = Dispatcher()
    print d.dispatch({'endpoint': 'X'})
