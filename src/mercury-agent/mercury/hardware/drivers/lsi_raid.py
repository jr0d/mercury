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

# Temporary baseline driver for LSI/PERC MegaRAID SAS adapters
# Next iteration will harness stor/percCLI which has JSON output capabilities

import logging

from mercury.hardware.raid.interfaces.lsi.megaraid.megacli import \
    LSIRaid, count_adapters

from mercury.hardware import platform_detection
from mercury.hardware.drivers import driver, PCIDriverBase

log = logging.getLogger(__name__)


def get_lsi_object(handler, adapter):
    from mercury.agent.configuration import agent_configuration

    kwargs = {'adapter': adapter}
    megacli_path = agent_configuration.get('hardware', {}).get('raid', {}).get('megacli_path')
    if megacli_path:
        log.debug('Using megacli_path: %s' % megacli_path)
        kwargs['megacli_path'] = megacli_path

    return handler(**kwargs)


@driver()
class MegaRaidSASDriver(PCIDriverBase):
    name = 'megaraid_sas'  # named after the kernel module
    driver_type = 'raid'
    _handler = LSIRaid

    @classmethod
    def probe(cls, pci_data):
        raid_pci_devices = platform_detection.get_raid_controllers(pci_data)
        owns = list()

        for device in raid_pci_devices:
            if cls.check(device):
                owns.append(device['slot'])
        return owns

    @classmethod
    def check(cls, pci_device):
        return pci_device['driver'] == cls.name

    def inspect(self):
        adapters = list()
        for a in range(count_adapters()):
            raid_handler = get_lsi_object(self._handler, adapter=a)
            _a = {
                    'adapter_handler': self.name,
                    'drives': raid_handler.pdisks,
                    'total_drives': raid_handler.count_physical_disks(),
                    'total_size': 0,  # This field is mostly useless, see spec
                    'configuration': {'arrays': raid_handler.vdisks}
            }
            adapters.append(_a)

        return adapters
