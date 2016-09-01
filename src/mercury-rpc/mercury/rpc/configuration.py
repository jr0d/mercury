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

from mercury.common.configuration import get_configuration
from mercury.common.mongo import get_collection


RPC_CONFIG_FILE = 'mercury-rpc.yaml'

TASK_QUEUE = 'rpc_tasks'

rpc_configuration = get_configuration(RPC_CONFIG_FILE)

db_configuration = rpc_configuration.get('db', {})


def get_tasks_collection(connection=None):
    tasks_db = db_configuration.get('tasks_mongo_db', 'test')
    tasks_collection = db_configuration.get('tasks_mongo_collection', 'rpc_tasks')
    tasks_servers = db_configuration.get('tasks_mongo_servers', 'localhost')
    replica_set = db_configuration.get('tasks_replica_set')

    return get_collection(
        tasks_db,
        tasks_collection,
        connection=connection,
        server_or_servers=tasks_servers,
        replica_set=replica_set
    )


def get_jobs_collection(connection=None):
    jobs_db = db_configuration.get('jobs_mongo_db', 'test')
    jobs_collection = db_configuration.get('jobs_mongo_collection', 'rpc_jobs')
    jobs_servers = db_configuration.get('jobs_mongo_servers', 'localhost')
    replica_set = db_configuration.get('jobs_replica_set')

    return get_collection(
        jobs_db,
        jobs_collection,
        connection=connection,
        server_or_servers=jobs_servers,
        replica_set=replica_set
    )
