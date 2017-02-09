# Copyright 2017 Rackspace
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

import json
import os

from mercury.hardware.raid.abstraction.api import (
    RAIDAbstractionException,
    RAIDActions,
)

from ..base import MercuryAgentUnitTest


class DummyImplementation(RAIDActions):
    def __init__(self):
        super(DummyImplementation, self).__init__()

        with open(os.path.join(os.path.dirname(__file__), '../resources/dummy.json')) as fp:
            self.dummy_data = json.load(fp)

    def transform_adapter_info(self, adapter_index):
        try:
            return self.dummy_data[adapter_index]
        except IndexError:
            raise RAIDAbstractionException('...')

    def create(self, adapter, level, drives=None, size=None, array=None):
        return True

    def delete_logical_drive(self, adapter, array, ld):
        return True

    def clear_configuration(self, adapter):
        return True

    def add_spares(self, adapter, array, drives):
        return True

    @staticmethod
    def sort_drives(drives):
        drives.sort(key=lambda x: '{}-{:05}-{:05}'.format(
            x['extra']['port'], int(x['extra']['box']),  int(x['extra']['bay'])))


class MercuryRAIDAbstractionAPITest(MercuryAgentUnitTest):
    def setUp(self):
        super(MercuryRAIDAbstractionAPITest, self).setUp()
        self.dummy = DummyImplementation()
        self.abstract = RAIDActions()

    def test_raid_calc(self):
        _calc = self.dummy.raid_calculator

        tests = [
            dict(level='0', number=1, size=300, result=300),
            dict(level='1', number=2, size=300, result=300),
            dict(level='5', number=3, size=300, result=600),
            dict(level='6', number=6, size=300, result=1200),
            dict(level='10', number=4, size=300, result=600),
            dict(level='1+0', number=4, size=300, result=600),
            dict(level='50', number=6, size=300, result=1200),
            dict(level='60', number=8, size=300, result=1200)
        ]

        for test in tests:
            assert _calc(test['level'], test['number'], test['size']) == test['result']

        self.assertRaises(RAIDAbstractionException, _calc, *('20', 0, 0, 0))

    def test_raid_minimums(self):
        _min = self.dummy.raid_minimums
        tests = [
            dict(level='1', _pass=2, fail=1),
            dict(level='5', _pass=3, fail=2),
            dict(level='6', _pass=4, fail=3),
            dict(level='10', _pass=4, fail=7),
            dict(level='1+0', _pass=4, fail=3),
            dict(level='50', _pass=6, fail=5),
            dict(level='60', _pass=8, fail=7)
        ]

        for test in tests:
            # Will raise on failure
            self.assertEqual(_min(test['level'], test['_pass']), None)

        for test in tests:
            self.assertRaises(RAIDAbstractionException, _min, *(test['level'], test['fail']))

        self.assertRaises(RAIDAbstractionException, _min, *('60', 11))

    def test_create(self):
        # Create new array
        assert self.dummy.create_logical_drive(adapter=0, level='0', drives='9, 10', size='10GiB')
        assert self.dummy.create_logical_drive(adapter=0, level='0', drives='9-11', size='10%FREE')
        assert self.dummy.create_logical_drive(adapter=0, level='0', drives=9)
        assert self.dummy.create_logical_drive(adapter=0, level='0', drives=[9, 10, 11])

        # Update existing array
        assert self.dummy.create_logical_drive(adapter=0, level='0', array=0, size='10%FREE')

        test_exception_args = [
            (0, '0', '9, 10', '100TiB'),  # Size is too big
            (0, '0'),  # Neither drives or array is specified
            (0, '0', None, '10GiB', 100),  # Array index is invalid
            (1, '0', None, '1MiB', 0),  # Not enough free space
            (0, '0', None, '100TiB', 0),  # Array does not have enough free space
            (0, '0', None, '100%', 0),  # Only %FREE is supported
            (0, '0', '11-9', None, None),  # range is negative
            (0, '0', '9-XXX', None, None),  # range is nonsense
            (0, '0', '9_10', None, None),  # range needs a '-'
            (0, '0', '9-10-11', None, None),  # too many '-'
            (0, '0', 'all', None, None),  # All drives are not available
            (0, '0', 'unassigned', None, None),  # One of the unassigned drives is marked FAILED
        ]

        for args in test_exception_args:
            self.assertRaises(RAIDAbstractionException, self.dummy.create_logical_drive, *args)

    def test_abstract(self):
        # Silly tests for 'coverage'
        self.assertRaises(NotImplementedError, self.abstract.transform_adapter_info, *(0, ))
        self.assertRaises(NotImplementedError, self.abstract.create, *(0, 0))
        self.assertRaises(NotImplementedError, self.abstract.delete_logical_drive, *(0, 0, 0))
        self.assertRaises(NotImplementedError, self.abstract.clear_configuration, *(0, ))
        self.assertRaises(NotImplementedError, self.abstract.add_spares, *(0, 0, 0))
        self.abstract.sort_drives([0, 1, 2, 3])

    def test_get_drives(self):
        assert self.dummy.get_unassigned(0)

        self.assertRaises(RAIDAbstractionException,
                          self.dummy.get_unassigned, *(100, ))  # invalid adapter

    def test_add_index(self):
        # Tests that indexes are added to drives
        drives = self.dummy.get_all_drives(0)
        for idx in range(len(drives)):
            assert idx == drives[idx]['index']
