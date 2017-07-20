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

# Temporary baseline driver for LSI/PERC MegaRAID SAS adapters
# Next iteration will harness stor/percCLI which has JSON output capabilities

import logging

from mercury.agent.configuration import agent_configuration

from mercury.hardware import platform_detection
from mercury.hardware.drivers import driver, PCIDriverBase
from mercury.hardware.raid.abstraction.api import RAIDActions, RAIDAbstractionException
from mercury.hardware.raid.interfaces.megaraid.storcli import Storcli, StorcliException

log = logging.getLogger(__name__)


class MegaRAIDActions(RAIDActions):
    # Drives have many more statuses than we care about
    # This information will be preserved in extra
    drive_status_map = {
        'DHS': 'OK',  # Dedicated Hotspare
        'UGood': 'OK',
        'GHS': 'OK',  # Global Hotspare
        'UBad': 'Failed',
        'Onln': 'OK',
        'Offln': 'Failed'
    }

    logical_drive_map = {
        'Rec': 'RECOVERING',
        'Pdgd': 'DEGRADED',
        'dgrd': 'DEGRADED',
        'OPtl': 'OK'
    }

    def __init__(self):
        """ MegaRAID support for RAID abstraction.
        This class is using the mercury native storcli interface. The interface is very thin.
        As such, vendor_info may need a little more cleanup in comparison to SmartArray
        """
        super(MegaRAIDActions, self).__init__()
        self.storcli = Storcli(binary_path=agent_configuration.get(
            'hardware', {}).get(
            'raid', {}).get(
            'storcli_path') or 'storcli')

    @staticmethod
    def get_vendor_info(adapter):
        return {
            'general': adapter['Basics'],
            'version_info': adapter['Version'],
            'bus': adapter['Bus'],
            'status': adapter['Status'],
            'supported_adapter_ops': adapter['Supported Adapter Operations'],
            'supported_pd_ops': adapter['Supported PD Operations'],
            'supported_vd_ops': adapter['Supported VD Operations'],
            'bbu_info': adapter['BBU_Info']
        }

    def parse_topology(self, topology):
        pass

    def parse_vd_list(self, vd_list):
        pass

    def transform_adapter_info(self, adapter_index):
        """
        Transforms Storcli.controllers[adapter_index] into standard form
        :param adapter_index:
        :return: Adapter details in standard from
        """
        try:
            adapter = self.storcli.controllers[adapter_index]
        except IndexError:
            raise RAIDAbstractionException('Controller does not exist')

        adapter_details = {
            'name': adapter['Basics']['Model'],
            'provider': 'megaraid',
            'vendor_info': self.get_vendor_info(adapter)
        }

        return adapter_details


@driver()
class MegaRaidSASDriver(PCIDriverBase):
    name = 'megaraid_sas'  # named after the kernel module
    driver_type = 'raid'
    _handler = MegaRAIDActions
    wants = 'pci'

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
        adapters = []

        for idx in range(len(self.devices)):
            adapters.append(self.handler.get_adapter_info(idx))

        return adapters
