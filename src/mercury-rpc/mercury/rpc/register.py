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
from mercury.common.transport import SimpleRouterReqService
from mercury.common.configuration import get_configuration
from mercury.rpc.db import ActiveInventoryDBController
from mercury.rpc.ping import spawn

log = logging.getLogger(__name__)

RPC_CONFIG_FILE = 'mercury-rpc.yaml'

class RegistrationService(SimpleRouterReqService):
    def __init__(self, collection):
        configuration = get_configuration(RPC_CONFIG_FILE)
        registration_service_bind_address = configuration.get('backend',
                                                              dict()).get('registration_service_url',
                                                                          'tcp://0.0.0.0:9002')
        super(RegistrationService, self).__init__(registration_service_bind_address)

        self.db_controller = ActiveInventoryDBController(collection)

    def process(self, message):
        if message.get('action') == 'register':
            return self.register(data=message.get('client_info'))
        return dict(error=True, message='Did not receive appropriate action')

    def register(self, data):
        if not self.db_controller.validate(data):
            log.error('Recieved invalid data')
            return dict(error=True, message='Invalid request')

        self.db_controller.insert(data)
        endpoint = 'tcp://%s:%s' % (data['rpc_address'], data['ping_port'])
        spawn(endpoint, data['mercury_id'], self.db_controller)

        return dict(error=False, message='Registration successful')


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s : %(levelname)s - %(name)s - %(message)s')

    from mercury.common.mongo import get_collection

    _collection = get_collection('test', 'rpc')

    rs = RegistrationService(_collection)
    rs.start()
