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
"""Module to unit test mercury.common.misc.iproute2"""

import mock
import pytest

import mercury.inspector.hwlib.iproute2 as ipr2
from tests.unit.base import MercuryAgentUnitTest


IPROUTE2_EXAMPLE_OUTPUT_LINES = [
'default via 192.168.1.1 dev br0  proto static  metric 425',
'192.168.1.0/24 dev br0  proto kernel  scope link  src 192.168.1.175  metric 425',
'192.168.122.0/24 dev virbr0  proto kernel  scope link  src 192.168.122.1 linkdown'
]

EXPECTED_EXAMPLE_ENTRIES = [
    {
        'via': '192.168.1.1',
        'dev': 'br0',
        'destination': 'default',
        'proto': 'static',
        'metric': '425'
    },
    {
        'src': '192.168.1.175',
        'destination': '192.168.1.0/24',
        'dev': 'br0',
        'proto': 'kernel',
        'scope': 'link',
        'metric': '425'
    },
    {
        'src': '192.168.122.1',
        'destination': '192.168.122.0/24',
        'dev': 'virbr0',
        'proto': 'kernel',
        'scope': 'link',
        'linkdown': True
    }
]


def construct_ipr2_with_fake_output(ipr_output, ip_path='/usr/sbin/ip'):
    """Get an IPRoute2 object with faked ip route output."""
    with mock.patch('mercury.common.helpers.cli.find_in_path') as \
            find_in_path_mock:
        find_in_path_mock.return_value = ip_path
        with mock.patch('mercury.common.helpers.cli.run') as run_mock:
            run_mock.return_value = ipr_output
            return ipr2.IPRoute2()


class MercuryHwlibIPRoute2UnitTests(MercuryAgentUnitTest):
    """Unit tests for mercury.common.misc.iproute2"""
    def test_example_output_parsing(self):
        """Test if IPRoute2 parsed the example output correctly."""
        ipr = construct_ipr2_with_fake_output(
            '\n'.join(IPROUTE2_EXAMPLE_OUTPUT_LINES))
        result_table = ipr.table

        assert isinstance(result_table, list)
        assert len(result_table) == 3

        for index in range(0, len(result_table)):
            assert result_table[index] == EXPECTED_EXAMPLE_ENTRIES[index]

    def test_modified_example_parsing(self):
        """Test another case of IPRoute2 parsing."""
        new_test_output = '\n'.join(IPROUTE2_EXAMPLE_OUTPUT_LINES[0:2])
        ipr = construct_ipr2_with_fake_output(new_test_output)
        result_table = ipr.table

        assert isinstance(result_table, list)
        assert len(result_table) == 2

        for index in range(0, 2):
            assert result_table[index] == EXPECTED_EXAMPLE_ENTRIES[index]

    def test_ipr_output_is_malformed(self):
        """Test what happens if `ip route` output is malformed."""
        test_output = 'this is not good ip route output :('
        with pytest.raises(Exception):
            construct_ipr2_with_fake_output(test_output)
