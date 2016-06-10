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
import msgpack
import threading
import time
import zmq


RETRIES = 5  # TODO: YAML
PING_TIMEOUT = 2500  # TODO: YAML
BACK_OFF = .42


class Lock(object):
    # TODO: Implement dead-lock detection
    def __init__(self):
        self.lock = threading.Lock()

    def acquire(self):
        return self.lock.acquire(True)  # block on acquire

    def release(self):
        self.lock.release()


class ActiveDBSyncList(object):
    def __init__(self):
        self.__data = []
        self.lock = Lock()

    def populate(self):
        pass

