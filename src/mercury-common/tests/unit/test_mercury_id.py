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

import mercury.common.mercury_id as m_id

from .base import MercuryCommonUnitTest


class MercuryIdUnitTest(MercuryCommonUnitTest):
    def test_dmi_methods(self):
        dmi_keys = ('product_uuid', 'chassis_asset_tag', 'chassis_serial',
                    'board_asset_tag', 'board_serial')
        fake_dmi = { key : ''.join(['fake_', key]) for key in dmi_keys }
        result = m_id.dmi_methods(fake_dmi)
        assert result is not None
