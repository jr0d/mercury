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

from hpssa.hpssa import HPSSA

from mercury.agent.configuration import agent_configuration

from mercury.hardware import platform_detection
from mercury.hardware.drivers import driver, PCIDriverBase
from mercury.hardware.raid.abstraction.api import RAIDActions, RAIDAbstractionException


class SmartArrayActions(RAIDActions):
    logical_drive_status_map = {
        'OK': 'OK',
        'Recovering': 'RECOVERING',
        'Interim Recovery Mode': 'DEGRADED',
        'Failed': 'FAILED'
    }

    physical_drive_status_map = {
        'OK': 'OK',
        'Rebuilding': 'REBUILDING',
        'Failed': 'FAILED'
    }

    def __init__(self):
        super(SmartArrayActions, self).__init__()
        self.hpssa = HPSSA(hpssa_path=agent_configuration.get(
            'hardware', {}).get(
            'raid', {}).get(
            'hpssacli_path') or 'hpssacli')

    @staticmethod
    def get_vendor_info(adapter):
        """
        :param adapter:
        :return: vendor_details
        """
        vendor_details = adapter.copy()

        # Configuration is transformed and top level, so remove the vendor configuration
        del vendor_details['configuration']

        # Drives can be found in the top level configuration
        del vendor_details['drives']

        # name is stored top level
        del vendor_details['name']

        return vendor_details

    def transform_logical_drives(self, logical_drives):
            return [{
                'status': self.logical_drive_status_map.get(logical_drive['status'], 'UNKNOWN'),
                'size': logical_drive['size'],
                'level': logical_drive['level'],
                'extra': {
                    'id': logical_drive['id'],
                    'progress': logical_drive['progress']
                }
            } for logical_drive in logical_drives]

    def convert_physical_drive(self, physical_drive):
        status = self.physical_drive_status_map.get(physical_drive['status'])
        if not status:
            raise RAIDAbstractionException(
                'Drive {port}:{box}:{bay} is in an unknown state: {status}'.format(
                    **physical_drive))

        new_physical_drive = {
            'size': physical_drive['size'],
            'status': status,
            'type': physical_drive['type'],
            'extra': {
                'port': physical_drive['port'],
                'box': physical_drive['box'],
                'bay': physical_drive['bay'],
            }
        }
        return new_physical_drive

    def transform_physical_drives(self, physical_drives):
        return [self.convert_physical_drive(physical_drive) for physical_drive in physical_drives]

    @staticmethod
    def get_array_index_from_letter(arrays, letter):
        for idx in range(len(arrays)):
            if arrays[idx]['extra']['letter'] == letter:
                return idx
        return -1

    def transform_configuration(self, original):
        configuration = {
            'arrays': [],
            'spares': [],
            'unassigned': []
        }

        for array in original['arrays']:
            configuration['arrays'].append({
                'free_space': array['free_space'],
                'extra': {
                    'letter': array['letter']
                },
                'logical_drives': self.transform_logical_drives(array['logical_drives']),
                'physical_drives': self.transform_physical_drives(array['physical_drives'])
            })

        #####################################################################################
        # hpssa spares look like this:
        #     [{'arrays': ['A'],
        #       'bay': '8',
        #       'box': '1',
        #       'port': '1I',
        #       'size': 300000000000,
        #       'status': 'OK',
        #       'type': 'SAS'}]
        # since this abstraction layer uses indexes for everything, we convert the letter
        # references to an index reference
        #####################################################################################

        for spare in original['spares']:
            array_indices = []
            for ref in spare['arrays']:
                idx = self.get_array_index_from_letter(configuration['arrays'], ref)
                if idx == -1:
                    raise RAIDAbstractionException('A spare is defined with an invalid array reference')
                array_indices.append(idx)

            spare_physical_drive = self.convert_physical_drive(spare)
            spare_physical_drive['target'] = array_indices
            configuration['spares'].append(spare_physical_drive)

        for unassigned in original['unassigned']:
            configuration['unassigned'].append(self.convert_physical_drive(unassigned))

        return configuration

    @staticmethod
    def get_slot(adapter_info):
        try:
            return int(adapter_info['vendor_info']['slot'])
        except KeyError:
            raise RAIDAbstractionException('Adapter is missing HP vendor/slot information')

    @staticmethod
    def get_letter_from_index(adapter_info, array_index):
        arrays = adapter_info['configuration']['arrays']

        try:
            our_array = arrays[array_index]
        except IndexError:
            raise RAIDAbstractionException('array {} does not exist'.format(array_index))

        # noinspection PyTypeChecker
        return our_array['extra']['letter']

    def transform_adapter_info(self, adapter_index):
        """
        Transforms python-hpssa adapter information into the standard format expected
        by RAIDActions
        :param adapter_index: list index of the adapter we are targeting
        :return: Adapter details in standard form
        """
        try:
            adapter = self.hpssa.adapters[adapter_index]
        except IndexError:
            raise RAIDAbstractionException('Adapter does not exist')

        adapter_details = {
            'name': adapter['name'],
            'provider': 'hspa',
            'vendor_info': self.get_vendor_info(adapter),
            'configuration': self.transform_configuration(adapter['configuration'])
        }

        return adapter_details

    @staticmethod
    def sort_drives(drives):
        """
        :param drives:
        :return:
        """
        drives.sort(key=lambda x: '{}-{:05}-{:05}'.format(
            x['extra']['port'], int(x['extra']['box']),  int(x['extra']['bay'])))

    @staticmethod
    def assemble_drive(drive):
        return '{port}:{box}:{bay}'.format(**drive['extra'])

    def create(self, adapter_info, level=None, drives=None, size=None, array=None):
        """
        Implementation of RAIDActions.create

        Called from RAIDActions.create_logical_drive

        :param adapter_info: transformed adapter_info
        :param level: RAID level supported by RAIDActions API
        :param drives: Converted drive target from RAIDActions create_logical_drive
            or None if array is specified
        :type drives: list
        :param size: python-size Size() object or None
        :param array: If specified, update the array that matches the index
        :return: result (returncode, stdout, stderr)
        :return type: AttributeString
        """
        size_mb = size and size.megabytes or 'max'

        slot = self.get_slot(adapter_info)
        if level == '10':
            level = '1+0'

        if drives:
            hpsa_targets = []
            for drive in drives:
                hpsa_targets.append(self.assemble_drive(drive))

            result = self.hpssa.create(slot, selection=','.join(hpsa_targets), raid=level, size=size_mb)

        else:
            array_letter = array['extra']['letter']
            result = self.hpssa.create(slot, raid=level, array_letter=array_letter, size=size_mb)

        return result

    def delete_logical_drive(self, adapter, array, logical_drive):
        """
        Implementation for RAIDActions.delete_logical_drive

        :param adapter: adapter index
        :param array: array index
        :param logical_drive: logical drive index
        :return:
        """
        adapter_info = self.get_adapter_info(adapter)
        slot = self.get_slot(adapter_info)
        arrays = adapter_info['configuration']['arrays']
        try:
            target = arrays[array]['logical_drives'][logical_drive]
        except IndexError:
            raise RAIDAbstractionException(
                'Logical Drive does not exist at {}:{}:{}'.format(adapter, array, logical_drive))

        return self.hpssa.delete_logical_drive(slot, target['extra']['id'])

    def clear_configuration(self, adapter):
        """
        Implementation of RAIDActions.clear_configuration
        :param adapter: adapter index
        :return:
        """
        return self.hpssa.delete_all_logical_drives(
            self.get_slot(self.get_adapter_info(adapter)))

    def add_spares(self, adapter, array, drives):
        """
        Implementation of RAIDActions.add_spares

        :param adapter: adapter index
        :param array: array index
        :param drives: RAIDActions drive selection
        :return:
        """
        adapter_info = self.get_adapter_info(adapter)
        slot = self.get_slot(adapter_info)

        array_letter = self.get_letter_from_index(adapter_info, array)
        target_drives = self.get_drives_from_selection(adapter, drives)

        return self.hpssa.add_spares(slot, array_letter,
                                     ','.join([self.assemble_drive(d) for d in target_drives]))


@driver()
class SmartArrayDriver(PCIDriverBase):
    name = 'hpssa'
    driver_type = 'raid'
    _handler = SmartArrayActions
    wants = 'pci'

    PCI_DEVICE_IDS = [
        "3239"  # Smart Array Gen9 Controllers
    ]

    @classmethod
    def probe(cls, pci_data):
        raid_pci_devices = platform_detection.get_raid_controllers(pci_data)
        if not platform_detection.has_smart_array_gen9(pci_data=raid_pci_devices):
            return

        owns = list()
        for device in raid_pci_devices:
            if cls.check(device):
                owns.append(device['slot'])
        return owns

    @classmethod
    def check(cls, pci_device):
        return pci_device['device_id'] in cls.PCI_DEVICE_IDS

    def inspect(self):
        adapters = []
        for idx in range(len(self.handler.hpssa.adapters)):
            _a = dict(**self.handler.get_adapter_info(idx))
            adapter_obj = self.handler.hpssa.adapters[idx]
            _a.update({
                'total_drives': adapter_obj.total_drives,
                'total_size': adapter_obj.total_size,
                'adapter_handler': self.name
            })

            adapters.append(_a)

        return adapters
