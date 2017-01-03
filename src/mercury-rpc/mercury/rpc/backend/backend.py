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

import asyncio
import logging

import motor.motor_asyncio
import zmq
import zmq.asyncio

from mercury.common.asyncio.transport import AsyncRouterReqService
from mercury.common.mongo import get_collection
from mercury.rpc.active_asyncio import active_state, ping_loop
from mercury.rpc.configuration import rpc_configuration, get_jobs_collection, get_tasks_collection
from mercury.rpc.db import ActiveInventoryDBController
from mercury.rpc.jobs.monitor import Monitor
from mercury.rpc.jobs.tasks import (
    complete_task,
    update_task
)
from mercury.rpc.ping import spawn

log = logging.getLogger(__name__)

RPC_CONFIG_FILE = 'mercury-rpc.yaml'


# TODO: Rewrite BackEndService as a general purpose message router


class BackEndService(AsyncRouterReqService):
    def __init__(self, active_db_collection, jobs_collection, tasks_collection):
        registration_service_bind_address = rpc_configuration.get('backend',
                                                                  {}).get('service_url',
                                                                          'tcp://0.0.0.0:9002')
        super(BackEndService, self).__init__(registration_service_bind_address)

        self.active_db_controller = ActiveInventoryDBController(active_db_collection)

        self.jobs_collection = jobs_collection
        self.tasks_collection = tasks_collection

    async def process(self, message):
        if message.get('action') == 'register':
            return await self.register(data=message.get('client_info'))
        elif message.get('action') == 'task_update':
            return await self.task_update(message.get('update_data'))
        elif message.get('action') == 'task_return':
            return await self.task_return(message.get('return_data'))
        return dict(error=True, message='Did not receive appropriate action')

    def spawn_pinger(self, mercury_id, address, port):
        endpoint = 'tcp://%s:%s' % (address, port)
        spawn(endpoint, mercury_id, self.active_db_controller)

    def reacquire(self):
        existing_documents = self.active_db_controller.query({}, projection={'mercury_id': 1,
                                                                             'rpc_address': 1,
                                                                             'ping_port': 1})
        for doc in existing_documents:
            log.info('Attempting to reacquire %s : %s' % (doc['mercury_id'], doc['rpc_address']))
            self.update_state(doc)

    async def register(self, data):
        if not self.active_db_controller.validate(data):
            log.error('Recieved invalid data')
            return dict(error=True, message='Invalid request')

        await self.active_db_controller.insert(data)

        self.update_state(data)

        return dict(error=False, message='Registration successful')

    async def task_update(self, update_data):
        """
        Update a task action string and optional progress metric
        :param update_data: {
            action: Pretty status
            progress: value between 0 and 1
        }
        :return:
        """
        task_id = self.get_key('task_id', update_data)
        update_task(task_id, update_data, tasks_collection=self.tasks_collection)

        return dict(message='Accepted')

    async def task_return(self, return_data):
        """Finish Job task with response data and status status
        :param return_data: {
            job_id:
            task_id:
            mercury_id:
            method:
            time_started:
            time_completed:
            data: {
            }
            status: SUCCESS|ERROR|EXCEPTION|TIMEOUT
            action: Pretty status
        }
        :return:
        """

        job_id = self.get_key('job_id', return_data)
        task_id = self.get_key('task_id', return_data)

        self.validate_required(['status', 'message', 'traceback_info'], return_data)

        complete_task(job_id,
                      task_id,
                      return_data,
                      jobs_collection=self.jobs_collection,
                      tasks_collection=self.tasks_collection)

        return dict(message='Accepted')

    @staticmethod
    def update_state(record):
        log.debug('Adding record, {mercury_id}, to active state'.format(**record))
        active_state.update({
            record['mercury_id']: {
                'mercury_id': record['mercury_id'],
                'rpc_address': record['rpc_address'],
                'rpc_address6': record['rpc_address6'],
                'ping_port': record['ping_port'],
                'last_ping': 0,
                'pinging': False
            }
        })


def get_connection_async(server_or_servers=None, replica_set=None):
    servers = server_or_servers
    if servers is not None:
        if not isinstance(servers, list):
            servers = [servers]
    log.info('Connecting to %s : replicaSet: %s' % (servers, replica_set))
    return motor.motor_asyncio.AsyncIOMotorClient(servers, replicaset=replica_set)


def rpc_backend_service():
    """
    Entry point

    :return:
    """
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s : %(levelname)s - %(name)s - %(message)s')
    logging.getLogger('mercury.rpc.ping').setLevel(logging.INFO)
    logging.getLogger('mercury.rpc.ping2').setLevel(logging.INFO)
    logging.getLogger('mercury.rpc.jobs.monitor').setLevel(logging.INFO)
    db_configuration = rpc_configuration.get('db', {})

    loop = zmq.asyncio.ZMQEventLoop()
    loop.set_debug(True)
    asyncio.set_event_loop(loop)

    connection = get_connection_async(server_or_servers=db_configuration.get('rpc_mongo_servers',
                                                                             'localhost'),
                                      replica_set=db_configuration.get('replica_set'))

    active_db_collection = get_collection(db_configuration.get('rpc_mongo_db',
                                                               'test'),
                                          db_configuration.get('rpc_mongo_collection',
                                                               'rpc'),
                                          connection)

    jobs_collection = get_jobs_collection(connection)
    tasks_collection = get_tasks_collection(connection)

    jobs_collection.create_index('ttl_time_completed', expireAfterSeconds=3600)
    tasks_collection.create_index('ttl_time_completed', expireAfterSeconds=3600)

    monitor = Monitor(jobs_collection, tasks_collection)
    monitor.start()

    server = BackEndService(active_db_collection, jobs_collection, tasks_collection)
    server.reacquire()
    asyncio.ensure_future(ping_loop(server.context, 30, 10, 2500, 5, .42, loop), loop=loop)
    try:
        loop.run_until_complete(server.start())
    finally:
        server.socket.close(0)
        server.context.destroy()
        monitor.kill()


if __name__ == '__main__':
    rpc_backend_service()
