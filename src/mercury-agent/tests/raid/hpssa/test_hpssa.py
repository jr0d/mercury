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

# TODO: Tests?

import os
import unittest

from mercury.hardware.raid.interfaces.hpsa.hpssa import (
    parse_show_config
)

path_of_test = os.path.dirname(__file__)

input_files = {
    'slot_config': [
        'show_slot_config_ex1.txt',
        'show_slot_config_error1.txt',
        'nothing.txt'
    ]
}


def join_input_file(k, f):
    l = input_files.get(k)
    if not l:
        raise Exception('Blast!')

    for file_name in l:
        if f == file_name:
            return os.path.join(path_of_test, f)


class TestHPSSA(unittest.TestCase):
    def test_parse_show_config(self):
        for input_file in input_files.get('slot_config'):
            assert parse_show_config(os.path.join(path_of_test, input_file))




