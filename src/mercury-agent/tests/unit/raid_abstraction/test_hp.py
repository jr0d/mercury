import json
import os

import mock

from hpssa.hpssa import Adapter

from mercury.hardware.drivers.hp_raid import (
    SmartArrayActions,
    SmartArrayDriver
)
from ..base import MercuryAgentUnitTest


# noinspection PyMethodMayBeStatic
# noinspection PyMethodOverriding
class MercurySmartArrayDriverTest(MercuryAgentUnitTest):
    def setUp(self):
        super(MercurySmartArrayDriverTest, self).setUp()
        with open(os.path.join(os.path.dirname(__file__), '../resources/adapters.json')) as fp:
            _adapters = json.load(fp)
            self.adapter_data = [Adapter(**a) for a in _adapters]

    def test_probe(self):
        with open(os.path.join(os.path.dirname(__file__), '../resources/pci_data.json')) as fp:
            pci_data = json.load(fp)

        assert SmartArrayDriver.probe(pci_data)

    def test_inspect(self):
        mock_hpssa = mock.MagicMock('hpssa.hpssa.HPSSA')
        mock_hpssa.adapters = self.adapter_data
        mock_hpssa.refresh = lambda: None
        smart_array_mock = mock.Mock('mercury.hardware.drivers.hp_raid.SmartArrayDriver')
        smart_array_mock.hpssa = mock_hpssa

        driver = smart_array_mock()

        data = driver.inspect()

        print(data)
        raise Exception('blah')
