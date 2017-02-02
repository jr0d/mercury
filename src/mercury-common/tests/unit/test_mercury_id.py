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

import pytest

import mercury.common.exceptions as m_exc
import mercury.common.mercury_id as m_id
from tests.unit.base import MercuryCommonUnitTest


def get_fake_dmi_dict():
    """Get a dmi dict test-fixture.

    :returns: A dictionary consumable by mercury_id.dmi_methods
    """
    dmi_keys = ('product_uuid', 'chassis_asset_tag', 'chassis_serial',
                'board_asset_tag', 'board_serial')
    return {key : ''.join(['fake_', key]) for key in dmi_keys}


class MercuryIdUnitTest(MercuryCommonUnitTest):
    """Unit tests for mercury.common.mercury_id module."""
    def test_dmi_methods(self):
        """Test dmi_methods(): When dmi information looks normal."""
        fake_dmi = get_fake_dmi_dict()
        assert m_id.dmi_methods(fake_dmi)

    def test_dmi_methods_disqualified(self):
        """Test dmi_methods(): the disqualified message is in the dmi dict."""
        for key in ['chassis_asset_tag', 'chassis_serial', 'board_asset_tag',
                    'board_serial']:
            fake_dmi = get_fake_dmi_dict()
            fake_dmi[key] = m_id.DMI_DISQUALIFIED_STRING
            fake_dmi['product_uuid'] = None
            assert m_id.dmi_methods(fake_dmi) is None

    def test_dmi_methods_chassis_and_board_not_set_as_pair(self):
        """Test dmi_methods(): Chassis or board DMI pair not set correctly."""
        fake_dmi = get_fake_dmi_dict()
        fake_dmi['product_uuid'] = None
        fake_dmi['chassis_asset_tag'] = None
        fake_dmi['board_asset_tag'] = None
        assert m_id.dmi_methods(fake_dmi) is None
