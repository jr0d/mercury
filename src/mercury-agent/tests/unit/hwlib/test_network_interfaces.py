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
"""Module to unit test mercury.inspector.hwlib.network_interfaces"""

import mock
import pytest

import netifaces

import mercury.inspector.hwlib.network_interfaces as net_ifs
from tests.unit.base import MercuryAgentUnitTest


FAKE_INTERFACE_LIST = ['lo', 'eno1', 'br0', 'virbr0', 'virbr0-nic', 'vnet0']


def fake_ifaddresses_func(interface):
    """Fake netifaces.ifaddresses()."""
    ifaddresses = {
        'lo': {
            netifaces.AF_LINK: [{'addr': '93:b9:b7:be:3c:00'}],
            netifaces.AF_INET: [{'addr': '127.0.0.1'}],
            netifaces.AF_INET6: [{'addr': '::1'}]
        },
        'eno1': {
            netifaces.AF_LINK: [{'addr': 'd4:a8:28:a2:19:2f'}],
            netifaces.AF_INET: [{'addr': '192.168.1.115'}],
            netifaces.AF_INET6: [{'addr': 'dead:beef::1'}]
        },
        'virbr0': {
            netifaces.AF_LINK: [{'addr': 'a8:b5:61:1c:de:39'}],
            netifaces.AF_INET: [{'addr': '192.168.122.1'}],
            netifaces.AF_INET6: [{'addr': 'dead:beed::1'}]
        }
    }
    return ifaddresses.get(interface, {})


class MercuryMiscNetworkInterfacesUnitTests(MercuryAgentUnitTest):
    """Unit tests for mercury.inspector.hwlib.network_interfaces"""
    def setUp(self):
        super(MercuryMiscNetworkInterfacesUnitTests, self).setUp()

    @mock.patch("netifaces.gateways")
    def test_get_default_interface(self, gateways_mock):
        """Tests for get_default_interface()"""
        gateways_mock.return_value = {}
        assert net_ifs.get_default_interface() == ''

        gateways_mock.return_value = {
            'default': {2: ('192.168.1.1', 'eth0')},
            2: [('192.168.1.1', 'eth0', True)]
        }
        assert net_ifs.get_default_interface() == 'eth0'

    @mock.patch("netifaces.ifaddresses")
    @mock.patch("netifaces.interfaces")
    def test_get_link_addresses(self, interfaces_mock, ifaddresses_mock):
        """Tests for get_link_addresses()"""
        interfaces_mock.return_value = FAKE_INTERFACE_LIST
        ifaddresses_mock.side_effect = fake_ifaddresses_func

        expected_output = [
            {'interface': 'lo', 'mac_address': '93:b9:b7:be:3c:00'},
            {'interface': 'eno1', 'mac_address': 'd4:a8:28:a2:19:2f'},
            {'interface': 'virbr0', 'mac_address': 'a8:b5:61:1c:de:39'},
        ]

        assert net_ifs.get_link_addresses(exclude_loopback=False) == \
            expected_output

    @mock.patch("netifaces.ifaddresses")
    @mock.patch("netifaces.interfaces")
    def test_get_ip4_network_info(self, interfaces_mock, ifaddresses_mock):
        """Tests for get_ipv4_network_info()."""
        interfaces_mock.return_value = FAKE_INTERFACE_LIST
        ifaddresses_mock.side_effect = fake_ifaddresses_func

        assert net_ifs.get_ipv4_network_info('not_an_interface') == []

        assert net_ifs.get_ipv4_network_info('eno1') == \
            [{'addr': '192.168.1.115'}]

    @mock.patch("netifaces.ifaddresses")
    @mock.patch("netifaces.interfaces")
    def test_get_ip6_network_info(self, interfaces_mock, ifaddresses_mock):
        """Tests for get_ipv6_network_info()."""
        interfaces_mock.return_value = FAKE_INTERFACE_LIST
        ifaddresses_mock.side_effect = fake_ifaddresses_func

        assert net_ifs.get_ipv6_network_info('not_an_interface') == []

        assert net_ifs.get_ipv6_network_info('virbr0') == \
            [{'addr': 'dead:beed::1'}]
