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

"""
From the pyudev docs:

    Once added, a filter cannot be removed anymore. Create a new object instead.

pyudev can be kind of silly, but I certainly don't feel like wrapping my own.
"""
import logging
import os
import pyudev

log = logging.getLogger(__name__)


class UDevHelper(object):
    def __init__(self):
        self.context = pyudev.Context()

    def get_monitor(self):
        """
        Because filters cannot be removed
        :return: fresh pyudev.Monitor
        """
        return pyudev.Monitor.from_netlink(self.context)

    def get_partitions(self):
        return self.context.list_devices(subsystem='block', DEVTYPE='partition')

    def get_disks(self):
        return self.context.list_devices(subsystem='block', DEVTYPE='disk')

    def find_partitions(self, device):
        """
        matches partitions belonging to a device.
        """

        devices = self.get_partitions()
        return devices.match_parent(pyudev.Device.from_device_file(self.context, device))

    def get_device_by_name(self, devname):
        try:
            udisk = pyudev.Device.from_device_file(self.context, devname)
        except OSError:
            return None
        return udisk

    def discover_valid_storage_devices(self, fc_enabled=True, loop_enabled=False):
        """
        Kind of ugly, but gets the job done. It strips devices we don't
        care about, such as cd roms, device mapper block devices, loop, and fibre channel.

        """

        disks = self.get_disks()
        pruned = list()

        for disk in disks:
            if not fc_enabled and 'fc' in disk.get('ID_BUS', ''):
                continue

            if not loop_enabled and disk.get('MAJOR') == '7':
                continue

            if disk.get('ID_TYPE') == 'cd':
                continue

            if disk.get('MAJOR') == '254':  # Device Mapper (LVM)
                continue

            if os.path.split(disk.get('DEVPATH', ''))[-1].startswith('ram'):
                continue

            pruned.append(disk)

        return pruned

    def yield_mapped_devices(self):
        disks = self.get_disks()
        for disk in disks:
            if disk.get('MAJOR') == '254':  # Device Mapper (LVM)
                yield disk

    @staticmethod
    def monitor_partition_by_devname(monitor, partition_id, action=None):
        monitor.filter_by('block', device_type="partition")
        for _, device in monitor:
            log.debug('Seen: %s' % list(device.items()))
            if action and device.get('ACTION') != action:
                log.debug('Action, %s, does not match %s' % (action, device.get('ACTION')))
                continue
            if device.get('UDISKS_PARTITION_NUMBER') == str(partition_id):
                return str(device['DEVNAME'])

    def get_network_devices(self):
        """ Returns a list of all network(ethernet/type 1] devices found on the system. """

        result = []

        for candidate in self.context.list_devices(subsystem='net'):
            try:
                if candidate.attributes.asint('type') == 1:
                    result.append(candidate)
            except KeyError:
                pass

        # let's go ahead and return it sorted..
        result.sort(key=lambda dev: dev.sys_name)
        return result

    @staticmethod
    def monitor_for_volume(monitor, lv_name):
        monitor.filter_by('block')
        for action, device in monitor:
            if device.get('DM_LV_NAME') == lv_name:
                return device
