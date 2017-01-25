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

from mercury.hardware.raid.abstraction.api import (
    RAIDAbstractionException,
    RAIDActions,
)

from ..base import MercuryAgentUnitTest


class DummyImplementation(RAIDActions):
    pass


class MercuryRAIDAbstractionAPITest(MercuryAgentUnitTest):
    def setUp(self):
        super(MercuryRAIDAbstractionAPITest, self).setUp()
        self.dummy = DummyImplementation()

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
