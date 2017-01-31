import json
import os
import random

import mock

from hpssa.hpssa import Adapter

from mercury.hardware.drivers.hp_raid import (
    RAIDAbstractionException,
    SmartArrayActions,
    SmartArrayDriver
)
from ..base import MercuryAgentUnitTest


def get_adapters():
    with open(os.path.join(os.path.dirname(__file__), '../resources/adapters.json')) as fp:
        return json.load(fp)


class DummySmartArrayActions(SmartArrayActions):
    def __init__(self):
        super(SmartArrayActions, self).__init__()
        self.hpssa = mock.Mock()
        self.hpssa.adapters = [Adapter(**a) for a in get_adapters()]
        self.hpssa.create = mock.Mock(return_value=True)
        self.hpssa.delete_logical_drive = mock.Mock(return_value=True)
        self.hpssa.delete_all_logical_drives = mock.Mock(return_value=True)
        self.hpssa.add_spares = mock.Mock(return_value=True)


class DummySmartArrayDriver(SmartArrayDriver):
    _handler = DummySmartArrayActions


# noinspection PyMethodMayBeStatic
# noinspection PyMethodOverriding
class MercurySmartArrayDriverTest(MercuryAgentUnitTest):
    def setUp(self):
        super(MercurySmartArrayDriverTest, self).setUp()

    def test_probe(self):
        with open(os.path.join(os.path.dirname(__file__), '../resources/pci_data.json')) as fp:
            pci_data = json.load(fp)

        assert SmartArrayDriver.probe(pci_data)
        assert not SmartArrayDriver.probe([])

    def test_inspect(self):
        driver = DummySmartArrayDriver()
        data = driver.inspect()
        assert data


class MercurySmartArrayActionsTest(MercuryAgentUnitTest):
    def setUp(self):
        super(MercurySmartArrayActionsTest, self).setUp()

        self.dummy_actions = DummySmartArrayActions()

    @mock.patch('mercury.hardware.drivers.hp_raid.HPSSA')
    def test_real_init(self, mock_hpssa):
        SmartArrayActions()

    def test_missing_array(self):
        original = get_adapters()[0]
        modified = original.copy()
        modified['configuration']['spares'][0]['arrays'] = ['Z']  # doesn't exist

        dummy_actions = DummySmartArrayActions()

        self.assertRaises(RAIDAbstractionException,
                          dummy_actions.transform_configuration, *(modified['configuration'], ))

    def test_get_slot_by_index(self):
        assert isinstance(self.dummy_actions.get_slot_by_index(0), int)
        self.assertRaises(RAIDAbstractionException, self.dummy_actions.get_slot_by_index, *(100, ))

        # Code (Jared) is paranoid and tests for missing vendor info
        temp_actions = DummySmartArrayActions()
        adapter_info = temp_actions.get_adapter_info(2)
        del adapter_info['vendor_info']['slot']

        self.assertRaises(RAIDAbstractionException, temp_actions.get_slot_by_index, *(2,))

    def test_get_letter_from_index(self):
        assert self.dummy_actions.get_letter_from_index(0, 0) == 'A'
        self.assertRaises(RAIDAbstractionException, self.dummy_actions.get_letter_from_index, *(0, 100))

    def test_sort_drives(self):
        drives = [
            {
                'index': 0,
                'extra': {
                    'port': '1I',
                    'box': '1',
                    'bay': '1'
                }
            },
            {
                'index': 1,
                'extra': {
                    'port': '2I',
                    'box': '1',
                    'bay': '1'
                }
            },
            {
                'index': 2,
                'extra': {
                    'port': '2I',
                    'box': '2',
                    'bay': '1'
                }
            },
            {
                'index': 3,
                'extra': {
                    'port': '3I',
                    'box': '1',
                    'bay': '1'
                }
            },
            {
                'index': 4,
                'extra': {
                    'port': '3I',
                    'box': '2',
                    'bay': '1'
                }
            },
        ]
        random.shuffle(drives)
        self.dummy_actions.sort_drives(drives)

        for idx in range(5):
            assert drives[idx]['index'] == idx

    def test_create(self):
        assert self.dummy_actions.create_logical_drive(0, '10', [10, 11, 12, 13])
        assert self.dummy_actions.create_logical_drive(0, '10', [10, 11, 12, 13], size='10GiB')
        assert self.dummy_actions.create_logical_drive(0, '6', array=0)

    def test_delete_logical_drive(self):
        assert self.dummy_actions.delete_logical_drive(0, 0, 0)
        self.assertRaises(RAIDAbstractionException, self.dummy_actions.delete_logical_drive, *(0, 0, 100))

    def test_clear_configuration(self):
        assert self.dummy_actions.clear_configuration(0)

    def test_add_spares(self):
        assert self.dummy_actions.add_spares(0, 0, [10, 11])
