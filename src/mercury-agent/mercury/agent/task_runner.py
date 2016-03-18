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
import time
import traceback
import threading

from mercury.agent.client import BackEndClient
from mercury.agent.configuration import agent_configuration
from mercury.common.exceptions import parse_exception, fancy_traceback_format, MercuryCritical
from mercury.common.transport import SimpleRouterReqClient

log = logging.getLogger(__name__)


class TaskRunner(object):
    def __init__(self, job_id, task_id, entry,
                 entry_args=None, entry_kwargs=None, lock=None):
        self.job_id = job_id
        self.task_id = task_id
        self.entry = entry
        self.args = entry_args or ()
        self.kwargs = entry_kwargs or {}
        self.lock = lock

        self.time_started = None
        self.time_completed = None

        rpc_backend = agent_configuration.get('remote', {}).get('rpc_service')
        if not rpc_backend:
            raise MercuryCritical('Missing rpc backend in local configuration')

        self.backend = BackEndClient(rpc_backend)

    def __run(self):
        self.time_started = time.time()
        traceback_info = None
        # noinspection PyBroadException
        try:
            return_data = self.entry(*self.args, **self.kwargs)
            # TODO: Create response contract for procedures
            if isinstance(return_data, dict) and return_data.get('error'):
                result = 'ERROR'
            else:
                result = 'SUCCESS'
        except Exception:
            exc_dict = parse_exception()
            log.error(fancy_traceback_format(exc_dict,
                                             'Critical error while running task: %s [%s], elapsed' % (
                                                 self.entry.__name__,
                                                 self.task_id)))
            traceback_info = exc_dict
            result = 'ERROR'
            return_data = None
        finally:
            if self.lock:
                log.debug('Releasing lock for %s' % self.lock.task_id)
                self.lock.release()

        self.time_completed = time.time()
        log.info('Task completed: %s [%s], elapsed %s' % (self.entry.__name__,
                                                          self.task_id,
                                                          self.time_completed - self.time_started))
        log.debug('Publishing response to: %s' % self.backend.zmq_url)

        response = self.backend.push_response({
            'result': result,
            'data': return_data,
            'traceback_info': traceback_info,
            'job_id': self.job_id,
            'task_id': self.task_id,
            'time_started': self.time_started,
            'time_completed': self.time_completed
        })
        log.debug('Dispatch successful : %s' % response)

    def run(self):
        log.info('Starting task: %s [%s]' % (self.entry.__name__, self.task_id))
        t = threading.Thread(target=self.__run)
        t.start()


if __name__ == '__main__':
    import uuid


    def subtract(a, b):
        return a - b


    task_runner = TaskRunner(uuid.uuid4(), uuid.uuid4(), subtract, entry_args=[9, 3])
    print task_runner.__dict__
    task_runner.run()
    print task_runner.__dict__
