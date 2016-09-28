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

"""
EVENTUAL CLASS HIERARCHY REPRESENTING INVENTORY/COMPUTER and ACTIVE/COMPUTER
"""
import json


class MercuryID(object):
    pass


class Computer(object):
    def __init__(self):
        self.raw_json_data = None
        self.computer_raw_object = None

    @classmethod
    def from_json(cls, json_data):
        obj = cls()
        obj.raw_json_data = json_data
        obj.computer_raw_object = json.loads(json_data)

        return obj
