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
import threading


log = logging.getLogger(__name__)


class TaskRunner(object):
    def __int__(self, job_id, task_id, entry, entry_args, entry_kwargs):
        self.job_id = job_id
        self.task_id = task_id
        self.entry = entry
        self.args = entry_args
        self.kwargs = entry_kwargs

        self.time_started, self.time_completed = None

    def __run(self):
        result = self.entry


    def run(self):
        log.info('Starting task: %s [%s]' % (self.entry.__name__, self.task_id))