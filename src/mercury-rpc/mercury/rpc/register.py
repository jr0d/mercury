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
from mercury.common.mongo import get_collection
from mercury.rpc.configuration import rpc_configuration
from mercury.rpc.db import ActiveInventoryDBController
from mercury.rpc.ping import spawn

log = logging.getLogger(__name__)

RPC_CONFIG_FILE = 'mercury-rpc.yaml'


class RegistrationService(SimpleRouterReqService):
    def __init__(self, collection):
        registration_service_bind_address = rpc_configuration.get('backend',
                                                                  {}).get('registration_service_url',
                                                                          'tcp://0.0.0.0:9002')
        super(RegistrationService, self).__init__(registration_service_bind_address)

        self.db_controller = ActiveInventoryDBController(collection)

    def process(self, message):
        if message.get('action') == 'register':
            return self.register(data=message.get('client_info'))
        return dict(error=True, message='Did not receive appropriate action')

    def spawn_pinger(self, mercury_id, address, port):
        endpoint = 'tcp://%s:%s' % (address, port)
        spawn(endpoint, mercury_id, self.db_controller)

    def reacquire(self):
        existing_documents = self.db_controller.query({}, projection={'mercury_id': 1,
                                                                      'rpc_address': 1,
                                                                      'ping_port': 1})
        for doc in existing_documents:
            log.info('Attempting to reacquire %s : %s' % (doc['mercury_id'], doc['rpc_address']))
            self.spawn_pinger(doc['mercury_id'], doc['rpc_address'], doc['ping_port'])

    def register(self, data):
        if not self.db_controller.validate(data):
            log.error('Recieved invalid data')
            return dict(error=True, message='Invalid request')

        self.db_controller.update(data)

        self.spawn_pinger(data['mercury_id'], data['rpc_address'], data['ping_port'])

        return dict(error=False, message='Registration successful')


def rpc_backend_register_service():
    """
    Entry point

    :return:
    """
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s : %(levelname)s - %(name)s - %(message)s')
    db_configuration = rpc_configuration.get('db', {})
    collection = get_collection(db_configuration.get('rpc_mongo_db',
                                                     'test'),
                                db_configuration.get('rpc_mongo_collection',
                                                     'rpc'),
                                server_or_servers=db_configuration.get('rpc_mongo_servers',
                                                                       'localhost'),
                                replica_set=db_configuration.get('replica_set'))

    server = RegistrationService(collection)
    server.reacquire()
    server.bind()
    server.start()


if __name__ == '__main__':
    rpc_backend_register_service()

