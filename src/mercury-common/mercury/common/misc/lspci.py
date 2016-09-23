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

import shlex
import subprocess


ETHERNET_CONTROLLER = '0200'
NETWORK_CONTROLLER = '0280'
FIBRE_CHANNEL = '0c04'
RAID_CONTROLLER = '0104'


class LSPCIError(Exception):
    pass


def lspci_run(arguments='-mm'):
    """
    Runs lspci and returns the output.
    :param arguments: Arguments you want to pass to lspci default = '-mm'
    :return: stdout from lspci command
    :except: LSPCIException on non-zero return code
    """
    cmd = shlex.split('lspci ' + arguments)

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()

    if p.returncode:
        raise LSPCIError('[%d] %s' % (p.returncode, err))

    return out


def parse_nnvmmk():
    """
    Runs lspci -nnvmmk and parses the output into a list of dictionaries.
    :return: a list of dicts with the following keys
    slot
    vendor_name
    device_name
    svendor_name
    sdevice_name
    vendor_id
    device_id
    svendor_id
    sdevice_id
    revision
    progif
    driver
    :except:
    """
    out = lspci_run('-nnvmmk')

    pcibus = list()

    def get_id(line):
        """
        Gets an id from a line that looks like this:
            Intel Corporation [8086]
        where 8086 is the id
        It should also work if something like this happens:
        2nd Generation Core Processor Family DRAM [not_and_id] Controller [0104]
        :param line:
        :return:
        """
        hush = line.split('[')
        if not len(hush):
            return None
        return hush[-1].strip(']')

    def get_name(line):
        hush = line.split('[')
        return '['.join(hush[0:-1]).strip()

    out = out.decode()
    blocks = out.split('\n\n')

    for block in blocks:
        device = dict()
        for element in block.splitlines():
            split_element = element.split(':')
            key = split_element[0]
            data = ':'.join(split_element[1:]).strip()
            if key == 'Slot':
                device['slot'] = data
                continue
            if key == 'Class':
                device['class_name'] = get_name(data)
                device['class_id'] = get_id(data)
                continue
            if key == 'Vendor':
                device['vendor_name'] = get_name(data)
                device['vendor_id'] = get_id(data)
                continue
            if key == 'Device':
                device['device_name'] = get_name(data)
                device['device_id'] = get_id(data)
                continue
            if key == 'SVendor':
                device['svendor_name'] = get_name(data)
                device['svendor_id'] = get_id(data)
                continue
            if key == 'SDevice':
                device['sdevice_name'] = get_name(data)
                device['sdevice_id'] = get_id(data)
                continue
            if key == 'Rev':
                device['revision'] = data
                continue
            if key == 'ProgIf':
                device['progif'] = data
                continue
            if key == 'Driver':
                device['driver'] = data

        if not device:
            continue
        pcibus.append(device)

    return pcibus


class PCIDevice(dict):
    def __init__(self,
                 slot=None,
                 class_id=None,
                 vendor_id=None,
                 device_id=None,
                 class_name='',
                 vendor_name='',
                 device_name='',
                 svendor_name=None,
                 svendor_id=None,
                 sdevice_name=None,
                 sdevice_id=None,
                 revision=None,
                 progif=None,
                 driver=None):
        if None in [slot, class_id, vendor_id, device_id]:
            raise LSPCIError(
                'slot, class_id, vendor_id, and device_id are required.')
        super(PCIDevice, self).__init__()
        self.slot = slot
        self.class_id = class_id
        self.vendor_id = vendor_id
        self.device_id = device_id
        self.class_name = class_name
        self.vendor_name = vendor_name
        self.device_name = device_name
        self.svendor_name = svendor_name
        self.svendor_id = svendor_id
        self.sdevice_name = sdevice_name
        self.sdevice_id = sdevice_id
        self.revision = revision
        self.progif = progif
        self.driver = driver

    def __getattr__(self, key):
        try:
            return self[key]
        except AttributeError:
            return None

    def __setattr__(self, key, value):
        self[key] = value


class PCIBus(list):
    def __init__(self, sudo=False):
        super(PCIBus, self).__init__()
        for it in parse_nnvmmk():
            self.append(PCIDevice(**it))

    def get_devices_by_class(self, class_id):
        sub_li = list()
        for device in self:
            if device.get('class_id') == class_id:
                sub_li.append(device)
        return sub_li

    def has_device_class(self, class_id):
        for device in self:
            if device.get('class_id') == class_id:
                return True
        return False

    def get_devices_by_vendor(self, vendor_id):
        sub_li = list()
        for device in self:
            if device.get('vendor_id') == vendor_id:
                sub_li.append(device)
        return sub_li

    def get_fibre_channel_devices(self):
        return self.get_devices_by_class(FIBRE_CHANNEL)

    def has_fibre_channel(self):
        return self.has_device_class(FIBRE_CHANNEL)

    def get_ethernet_devices(self):
        return self.get_devices_by_class(ETHERNET_CONTROLLER)

    def get_network_devices(self):
        return self.get_devices_by_class(NETWORK_CONTROLLER)

    def has_raid_bus_controller(self):
        return self.has_device_class(RAID_CONTROLLER)

    def get_raid_bus_controllers(self):
        return self.get_devices_by_class(RAID_CONTROLLER)
