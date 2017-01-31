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

from mercury.hardware import platform_detection
from mercury.hardware.drivers import driver, PCIDriverBase
from mercury.hardware.raid.abstraction.api import RAIDActions, RAIDAbstractionException


class SmartArrayActions(RAIDActions):
    ld_status_map = {
        'OK': 'OK',
        'Recovering': 'RECOVERING',
        'Interim Recovery Mode': 'DEGRADED',
        'Failed': 'FAILED'
    }

    pd_status_map = {
        'OK': 'OK',
        'Rebuilding': 'REBUILDING',
        'Failed': 'FAILED'
    }

    def __init__(self):
        super(SmartArrayActions, self).__init__()
        self.hpssa = HPSSA()

    @staticmethod
    def get_vendor_info(adapter):
        """
        :param adapter:
        :return: vendor_details
        """
        vendor_details = adapter.copy()
        del vendor_details['configuration']
        del vendor_details['drives']
        del vendor_details['name']

        return vendor_details

    def transform_ld(self, logical_drives):
        _lds = []
        for logical_drive in logical_drives:
            _ld = {
                'status': self.ld_status_map.get(logical_drive['status'], 'UNKNOWN'),
                'size': logical_drive['size'],
                'level': logical_drive['level'],
                'extra': {
                    'id': logical_drive['id'],
                    'progress': logical_drive['progress']
                }
            }
            _lds.append(_ld)

        return _lds

    def _convert_pd(self, pd):
        new_pd = {
            'size': pd['size'],
            'status': self.pd_status_map.get(pd['status'], 'UNKNOWN'),
            'type': pd['type'],
            'extra': {
                'port': pd['port'],
                'box': pd['box'],
                'bay': pd['bay'],
            }
        }
        return new_pd

    def transform_pd(self, physical_drives):
        _pds = []
        for physical_drive in physical_drives:
            _pds.append(self._convert_pd(physical_drive))
        return _pds

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
                'logical_drives': self.transform_ld(array['logical_drives']),
                'physical_drives': self.transform_pd(array['physical_drives'])
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

            spare_pd = self._convert_pd(spare)
            spare_pd['target'] = array_indices
            configuration['spares'].append(spare_pd)

        for unassigned in original['unassigned']:
            configuration['unassigned'].append(self._convert_pd(unassigned))

        return configuration

    def get_slot_by_index(self, adapter_index):
        adapter_info = self.get_adapter_info(adapter_index)
        try:
            return int(adapter_info['vendor_info']['slot'])
        except (KeyError, IndexError) as e:
            raise RAIDAbstractionException('Cannot retrieve slot info for {} : {}'.format(adapter_index, e))

    def get_letter_from_index(self, adapter_index, array_index):
        adapter_info = self.get_adapter_info(adapter_index)
        arrays = adapter_info['configuration']['arrays']

        try:
            array = arrays[array_index]
        except IndexError:
            raise RAIDAbstractionException('array {} does not exist'.format(array_index))

        # noinspection PyTypeChecker
        return array['extra']['letter']

    def transform_adapter_info(self, adapter_index):
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

    def create(self, adapter, level=None, drives=None, size=None, array=None):
        # Refresh the backend object
        self.hpssa.refresh()

        if size:
            size_mb = size.megabytes
        else:
            size_mb = 'max'

        slot = self.get_slot_by_index(adapter)
        if level == '10':
            level = '1+0'

        if drives:
            hpsa_targets = []
            for drive in drives:
                hpsa_targets.append(self.assemble_drive(drive))

            r = self.hpssa.create(slot, selection=','.join(hpsa_targets), raid=level, size=size_mb)

        else:
            array_letter = array['extra']['letter']
            r = self.hpssa.create(slot, raid=level, array_letter=array_letter, size=size_mb)

        return r

    def delete_logical_drive(self, adapter, array, ld):
        # paranoid synchronization
        self.hpssa.refresh()
        self.clear_cache()

        adapter_info = self.get_adapter_info(adapter)
        slot = self.get_slot_by_index(adapter)
        arrays = adapter_info['configuration']['arrays']
        try:
            target = arrays[array]['logical_drives'][ld]
        except IndexError:
            raise RAIDAbstractionException(
                'Logical Drive does not exist at {}:{}:{}'.format(adapter, array, ld))

        return self.hpssa.delete_logical_drive(slot, target['extra']['id'])

    def clear_configuration(self, adapter):
        self.hpssa.refresh()
        self.clear_cache()

        slot = self.get_slot_by_index(adapter)
        return self.hpssa.delete_all_logical_drives(slot)

    def add_spares(self, adapter, array, drives):
        self.hpssa.refresh()
        self.clear_cache()

        slot = self.get_slot_by_index(adapter)

        array_letter = self.get_letter_from_index(adapter, array)
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
