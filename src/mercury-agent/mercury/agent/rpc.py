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

from mercury.agent.capabilities import runtime_capabilities
from mercury.common.transport import SimpleRouterReqService

LOG = logging.getLogger(__name__)


class AgentService(SimpleRouterReqService):
    @staticmethod
    def error(code, message='', data=None):
        return {'status': code, 'message': message, 'data': data}

    @staticmethod
    def sync_response(data):
        return {'status': 0, 'message': '', 'data': data}

    @staticmethod
    def lookup_method(method):
        return runtime_capabilities.get(method)

    def validate_method_args(self, message, capability):
        num_args = capability.get('num_args')
        if num_args:
            if not len(message.get('args', 0)) == num_args:
                return self.error(4,
                                  'arguments for %s are not satisfied' %
                                  capability['name'])

        kwarg_names = capability.get('kwarg_names')
        if kwarg_names:
            message_kwargs = message.get('kwargs', {})
            if not isinstance(message_kwargs, dict):
                # could happen if message.kwargs is explicitly set to something other than a dict
                return self.error(4, 'kwargs is malformed in message')
            missing = []
            for k in kwarg_names:
                if k not in message_kwargs:
                    missing.append(k)
            if missing:
                return self.error(4, 'missing kwargs in message: %s' % ', '.join(missing))

    def process(self, message):
        LOG.debug('Processing request: %s' % message)

        category = message.get('category')
        if not category:
            return self.error(1, 'missing category, nothing to do')

        if category != 'rpc':
            # Remember, all of this is just a prototype

            # Need to finalize the agent contract
            return self.error(3, 'invalid category')

        method = message.get('method')
        if not method:
            return self.error(3, 'method not defined')

        capability = self.lookup_method(method)
        if not capability:
            return self.error(3, '%s method is not supported' % method)

        LOG.debug('Runtime selected: %s' % capability['name'])

        error = self.validate_method_args(message, capability)
        if error:
            return error

        args = message.get('args', ())
        kwargs = message.get('kwargs', {})

        task_id = message.get('task_id')
        job_id = message.get('job_id')

        if None in [task_id, job_id]:
            return self.error(3, 'message is incomplete, missing task_id/job_id')

        ret = capability['entry'](*args, **kwargs)
        return self.sync_response(data=ret)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    _bind_address = 'tcp://0.0.0.0:9003'
    agent_server = AgentService(_bind_address)
    print runtime_capabilities
    agent_server.start()
