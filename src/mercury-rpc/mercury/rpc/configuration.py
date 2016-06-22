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


RPC_CONFIG_FILE = 'mercury-rpc.yaml'

TASK_QUEUE = 'rpc_tasks'

rpc_configuration = get_configuration(RPC_CONFIG_FILE)

db_configuration = rpc_configuration.get('db', {})

print(db_configuration)