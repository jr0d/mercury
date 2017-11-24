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


BACKEND_CONFIG_FILE = 'mercury-backend.yaml'


def add_common_options(configuration):
    configuration.add_option('rpc.db.servers',
                             default='127.0.0.1:27017',
                             special_type=list,
                             help_string='Server or coma separated list of '
                                         'servers to connect to')

    configuration.add_option('rpc.db.name',
                             default='test',
                             help_string='The database for our collections')

    configuration.add_option('rpc.db.replica_name',
                             config_address='rpc.db.replica_name',
                             help_string='Optional replicaset name')

    configuration.add_option('rpc.db.jobs_collection',
                             config_address='rpc.db.jobs_collection',
                             default='rpc_jobs',
                             help_string='The collection for RPC jobs')

    configuration.add_option('rpc.db.tasks_collection',
                             config_address='rpc.db.tasks_collection',
                             default='rpc_tasks',
                             help_string='The collection for RPC tasks')

