# Copyright 2015 Jared Rodriguez (jared at blacknode dot net)
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


from hpssa import HPSSA

from mercury.hardware import platform_detection
from mercury.hardware.drivers import driver, PCIDriverBase


@driver()
class SmartArrayDriver(PCIDriverBase):
    name = 'hpssa'
    driver_type = 'raid'
    _handler = HPSSA

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
        hpssa = HPSSA()

        adapters = []
        for adapter in hpssa.adapters:
            _a = dict(**adapter)
            _a.update({
                'total_drives': adapter.total_drives,
                'total_size': adapter.total_size,
                'adapter_handler': self.name
            })

            adapters.append(_a)

        return adapters
