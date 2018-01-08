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
"""Unit tests for mercury_id module."""

import itertools

import pytest
import six

import mercury.common.exceptions as m_exc
import mercury.common.mercury_id as m_id
from tests.common.unit.base import MercuryCommonUnitTest


def get_fake_dmi_dict():
    """Get a dmi dict test-fixture.

    :returns: A dictionary consumable by mercury_id.dmi_methods
    """
    dmi_keys = ('product_uuid', 'chassis_asset_tag', 'chassis_serial',
                'board_asset_tag', 'board_serial')
    return {key: ''.join(['fake_', key]) for key in dmi_keys}


def get_fake_inspected_interfaces(num_interfaces=3):
    """Get a inspected interfaces dict test-fixture.

    :returns: A dictionary consumable by mercury_id.generate_mercury_id
    """
    def get_fake_interface(biosdevname='embedded_fake_bios_dev_name',
                           address='192.168.1.1'):
        """Get a fake interface to use to test mercury_id functionality."""
        return {
            'predictable_names': {'biosdevname': biosdevname},
            'address': address
        }

    return [get_fake_interface(name, address) for name, address in
            [('embedded_intel_nic_bios_%d' % n, '192.168.1.%d' % n) for n in
             range(0, num_interfaces)]]


# noinspection PyMethodMayBeStatic
class MercuryIdUnitTest(MercuryCommonUnitTest):
    """Unit tests for mercury.common.mercury_id module."""
    def test__get_embedded(self):
        """Test _get_embedded()"""
        inspected_interfaces = get_fake_inspected_interfaces()
        print(inspected_interfaces)
        embedded_interfaces = m_id._get_embedded(inspected_interfaces)

        inspected_interfaces[0]['predictable_names']['biosdevname'] = 'what'
        print(inspected_interfaces)
        should_be_changed_ei = m_id._get_embedded(inspected_interfaces)

        assert embedded_interfaces != should_be_changed_ei

    def test__dmi_methods(self):
        """Test _dmi_methods(): When dmi information looks normal."""
        fake_dmi = get_fake_dmi_dict()
        result = m_id._dmi_methods(fake_dmi)
        assert result is not None
        assert isinstance(result, six.string_types)

        # Make sure the ID changes given different information.
        fake_dmi['product_uuid'] = 'some_other_uuid'
        new_result = m_id._dmi_methods(fake_dmi)
        assert new_result is not None
        assert isinstance(result, six.string_types)
        assert result != new_result

    def test__dmi_methods_disqualified(self):
        """Test _dmi_methods(): the disqualified message is in the dmi dict."""
        for key in ['chassis_asset_tag', 'chassis_serial', 'board_asset_tag',
                    'board_serial']:
            fake_dmi = get_fake_dmi_dict()
            fake_dmi[key] = m_id.DMI_DISQUALIFIED_STRING
            fake_dmi['product_uuid'] = None
            assert m_id._dmi_methods(fake_dmi) is None

    def test__dmi_methods_dmi_pairs(self):
        """Test _dmi_methods(): Chassis or board DMI pair not set correctly."""
        fake_dmi = get_fake_dmi_dict()
        fake_dmi['product_uuid'] = None
        result = m_id._dmi_methods(fake_dmi)
        assert result is not None
        assert isinstance(result, six.string_types)

        fake_dmi['chassis_asset_tag'] = None
        second_result = m_id._dmi_methods(fake_dmi)
        assert second_result is not None
        assert isinstance(second_result, six.string_types)
        assert result != second_result

        fake_dmi['board_asset_tag'] = None
        assert m_id._dmi_methods(fake_dmi) is None

    def test_generate_mercury_id(self):
        """Test generate_mercury_id(): Normal cases."""
        inspected_dmi = get_fake_dmi_dict()
        inspected_interfaces = get_fake_inspected_interfaces(3)
        results = [m_id.generate_mercury_id(inspected_dmi,
                                            inspected_interfaces)]
        # Should key off of product_uuid

        # Same, but with a different result.
        inspected_dmi['product_uuid'] = 'something_else'
        results.append(m_id.generate_mercury_id(inspected_dmi,
                                                inspected_interfaces))

        # No product ID, but valid DMI information.
        inspected_dmi['product_uuid'] = None
        results.append(m_id.generate_mercury_id(inspected_dmi,
                                                inspected_interfaces))

        # There's invalid DMI information, so it goes to inspected interfaces.
        inspected_dmi['chassis_asset_tag'] = m_id.DMI_DISQUALIFIED_STRING
        results.append(m_id.generate_mercury_id(inspected_dmi,
                                                inspected_interfaces))

        # Embedded interfaces change.
        inspected_interfaces[0]['predictable_names']['biosdevname'] = \
            'something_else'
        results.append(m_id.generate_mercury_id(inspected_dmi,
                                                inspected_interfaces))

        # Make sure each result looks sane.
        for result in results:
            assert result is not None
            assert isinstance(result, six.string_types)

        # Make each mercury ID is unique.
        for first, second in itertools.combinations(results, 2):
            assert first != second

    def test_generate_mercury_id_raises(self):
        """Test generate_mercury_id(): When it should raise."""
        inspected_dmi = get_fake_dmi_dict()
        inspected_dmi['product_uuid'] = None
        inspected_dmi['chassis_asset_tag'] = m_id.DMI_DISQUALIFIED_STRING
        inspected_interfaces = get_fake_inspected_interfaces(0)
        with pytest.raises(m_exc.MercuryIdException):
            m_id.generate_mercury_id(inspected_dmi, inspected_interfaces)
