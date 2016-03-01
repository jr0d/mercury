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

from mercury.common.exceptions import fancy_traceback_format

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

    def __run(self):
        self.time_started = time.time()
        # noinspection PyBroadException
        try:
            result = self.entry(*self.args, **self.kwargs)
        except Exception as e:
            log.error(fancy_traceback_format(
                'Critical error while running task: %s [%s], elapsed' % (self.entry.__name__,
                                                                         self.task_id)))
            # Dispatch Error
            return
        finally:
            if self.lock:
                log.debug('Releasing lock for %s' % self.lock.task_id)
                self.lock.release()

        log.info('Task completed: %s [%s], elapsed' % (self.entry.__name__, self.task_id))
        self.time_completed = time.time()

        # Dispatch Result
        print result

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
