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

import logging
import threading
import time

from mercury.common.clients.rpc.backend import BackEndClient
from mercury.common.exceptions import fancy_traceback_short, parse_exception

log = logging.getLogger(__name__)


class TaskRunner(object):
    """
    """
    # TODO: Implement as a function
    def __init__(self, job_id, task_id, entry, backend_url,
                 entry_args=None, entry_kwargs=None, lock=None,
                 timeout=0, task_id_kwargs=False):
        self.job_id = job_id
        self.task_id = task_id
        self.entry = entry
        self.args = entry_args or ()
        self.kwargs = entry_kwargs or {}
        if task_id_kwargs:
            self.kwargs['task_id'] = self.task_id
        self.lock = lock
        self.timeout = timeout

        self.time_started = None
        self.time_completed = None

        self.backend = BackEndClient(backend_url)

    def __management_thread(self):
        """
        Async thread to support shared locking. Forks the entry into it's own memory space
        so that we can use signals to trigger timeouts
        :return:
        """
        self.time_started = time.time()
        traceback_info = None
        # noinspection PyBroadException
        try:
            return_data = self.entry(*self.args, **self.kwargs)
            # TODO: Create response contract for procedures
            if isinstance(return_data, dict) and return_data.get('error'):
                status = 'ERROR'
            else:
                status = 'SUCCESS'
        except Exception:
            exc_dict = parse_exception()
            log.error(fancy_traceback_short(exc_dict, 'Critical error while running task: %s [%s], elapsed' % (
                                            self.entry.__name__,
                                            self.task_id)),
                      extra={'task_id': self.task_id, 'job_id': self.job_id})
            traceback_info = parse_exception()
            status = 'ERROR'
            return_data = None
        finally:
            if self.lock:
                log.debug('Releasing lock for %s' % self.lock.task_id,
                          extra={'task_id': self.task_id, 'job_id': self.job_id})
                self.lock.release()

        self.time_completed = time.time()
        log.info('Task completed: %s [%s], elapsed %s' % (self.entry.__name__,
                                                          self.task_id,
                                                          self.time_completed - self.time_started),
                 extra={'task_id': self.task_id, 'job_id': self.job_id})
        log.debug('Publishing response to: %s' % self.backend.zmq_url,
                  extra={'task_id': self.task_id, 'job_id': self.job_id})

        response = self.backend.complete_task({
            'status': status,
            'message': return_data,
            'traceback_info': traceback_info,
            'job_id': self.job_id,
            'task_id': self.task_id,
            'time_started': self.time_started,
            'time_completed': self.time_completed,
            'action': 'Completed'
        })
        log.debug('Dispatch successful : %s' % response,
                  extra={'task_id': self.task_id, 'job_id': self.job_id})

    def run(self):
        log.info('Starting task: %s [%s]' % (self.entry.__name__, self.task_id),
                 extra={'task_id': self.task_id, 'job_id': self.job_id})
        t = threading.Thread(target=self.__management_thread, name='_{}_{}'.format(self.job_id, self.task_id))
        t.start()
