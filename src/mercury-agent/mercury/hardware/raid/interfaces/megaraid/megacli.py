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
Taken from kclient, one day we'll make all of these their own modules.. one day.

TODO: storecli, and not this.....
"""

import os

from mercury.common.helpers.cli import find_in_path, run
from mercury.inspector.hwlib.lspci import PCIBus

LSI_VENDOR_ID = '1000'
DEFAULT_MEGACLI_PATH = 'megacli'


def has_lsi_raid():
    pci_bus = PCIBus()
    controllers = pci_bus.get_raid_bus_controllers()
    for controller in controllers:
        if controller.vendor_id == LSI_VENDOR_ID:
            return True
    return False


def count_adapters():
    """Should probably be doing this with megacli
    :return:
    """
    pci_bus = PCIBus()
    if not has_lsi_raid():
        return 0
    controllers = pci_bus.get_raid_bus_controllers()
    cnt = 0
    for controller in controllers:
        if controller.vendor_id == LSI_VENDOR_ID:
            cnt += 1
    return cnt


class LSIRaidException(Exception):
    pass


class MegaCLI(object):
    def __init__(self, megacli_path=DEFAULT_MEGACLI_PATH,
                 adapter=0):

        self.clear = False
        self.adapter = adapter
        self.megacli_bin = find_in_path(megacli_path)
        if not self.megacli_bin:
            raise LSIRaidException('megacli binary is missing.')

        self.vdisks = None
        self.pdisks = None
        self.enclosure = None
        self.raw_adapter_info = None
        self.refresh()

    def refresh(self):
        self.pdisks = self.get_physical_disks(self.adapter)
        self.vdisks = self.get_virtual_disks(self.adapter)
        self.enclosure = self.get_enclosure_id(self.adapter)
        self.raw_adapter_info = self.get_adapter_raw()

        if not self.count_virtual_disks():
            self.clear = True

    def megacli(self, args, bufsize=1048567):
        cmd = [self.megacli_bin] + args.split()
        cmd = cmd + ['-NoLog']

        out = run(' '.join(cmd), bufsize=bufsize)
        return out, out.stderr, out.returncode

    def get_adapter_raw(self):
        out, err, ret = self.megacli('-AdpAllInfo -a%d' % self.adapter)
        if ret:
            raise LSIRaidException('Could not get adapter info. %s %s %s' % (ret, out, err))
        return out.splitlines()

    def clear_config(self):
        return self.megacli('-CfgClr -aAll')

    def init_logical_drives(self):
        return self.megacli('-LDInit -Start -LALL -aALL')

    def clear_foreign_configs(self):
        return self.megacli('-CfgForeign -Clear -a0')

    def count_physical_disks(self):
        out, err, ret = self.megacli('-PDGetNum -a%d' % self.adapter)
        for line in out.splitlines():
            if 'Adapter' in line:
                return int(line.split(':')[1].strip())
        return 0

    def count_virtual_disks(self):
        out, err, ret = self.megacli('-LDGetNum -a%d' % self.adapter)
        for line in out.splitlines():
            if 'Adapter' in line:
                return int(line.split(':')[1].strip())
        return 0

    def create_array(self, raid_level, drives):
        out = '-CfgLDAdd -r' + str(raid_level)
        array_list = ['%s:%d' % (self.enclosure, x) for x in drives]
        array_out = ' [' + ','.join(array_list) + ']'
        out = out + array_out + ' WB RA Cached -a%d' % self.adapter
        sout, err, ret = self.megacli(out)
        if ret:
            return dict(error=True, command=out, stdout=sout, stderr=err)
        return dict(error=False, command=out, stdout=sout, stderr=err)

    def add_hotspare(self, drive, array=None):
        out = '-PDHSP -Set'
        if array:
            out += ' -Dedicated -Array%d' % array
        out += ' -PhysDrv [%s:%d] -a%d' % (self.enclosure, drive, self.adapter)
        sout, err, ret = self.megacli(out)
        if ret:
            return dict(error=True, command=out, stdout=sout, stderr=err)
        return dict(error=False, command=out, stdout=sout, stderr=err)

    def create_span(self, raid_level, span_depth, drives):
        if len(drives) % span_depth:
            raise LSIRaidException('Wrong number of drives for span. drives[%d] %% span[%d] != 0' % (
                len(drives), span_depth
            ))
        span_list = list()
        for x in range(0, len(drives), span_depth):
            span_list.append(drives[x:x + span_depth])

        array_count = 1
        out = '-CfgSpanAdd -r' + str(raid_level) + ' '
        array_out = str()
        for array in span_list:
            array_list = ['%s:%d' % (self.enclosure, array[x]) for x in range(0, len(array))]
            array_out += '-Array%d[%s] ' % (array_count, ', '.join(array_list))
            array_count += 1

        out += array_out
        out += ' WB RA Cached -a%d' % self.adapter
        sout, err, ret = self.megacli(out)
        if ret:
            return dict(error=True, command=out, stdout=sout, stderr=err)
        return dict(error=False, command=out, stdout=sout, stderr=err)

    def get_enclosure_id(self, adapter=0):
        out, err, ret = self.megacli('-EncInfo -a%d' % adapter)
        for line in out.splitlines():
            if 'Device ID' in line:
                return int(line.split(':')[1].strip())
        return ""

    def get_pd_by_id(self, pid):
        for pd in self.pdisks:
            if pd['device_id'] == pid:
                return pd

    def get_pd_by_slot_number(self, num):
        for pd in self.pdisks:
            if pd['slot_number'] == num:
                return pd

    def get_physical_disks(self, adapter=0):
        disks = list()
        count = 0
        num = self.count_physical_disks()
        if not num:
            return dict()

        out, err, ret = self.megacli('-PdList -a%d' % adapter)
        for x in range(0, num):
            disk = dict()
            for line in out.splitlines()[count:]:
                if 'Device Id' in line:
                    disk['device_id'] = int(line.split(':')[1].strip())
                    count += 1
                    continue

                if 'Slot Number' in line:
                    disk['slot_number'] = int(line.split(':')[1].strip())
                    count += 1
                    continue

                if 'Raw Size' in line:
                    disk['size'] = float(line.split(':')[1].split()[0].strip())
                    disk['multiple'] = line.split(':')[1].split()[1].strip()
                    count += 1
                    continue

                if 'Media Error Count' in line:
                    disk['media_errors'] = int(line.split(':')[1].strip())
                    count += 1
                    continue

                if 'Other Error Count' in line:
                    disk['other_errors'] = int(line.split(':')[1].strip())
                    count += 1
                    continue

                if 'Predictive Failure Count' in line:
                    disk['predictive_errors'] = int(line.split(':')[1].strip())
                    count += 1
                    continue

                if 'Firmware state' in line:
                    disk['state'] = line.split(':', 1)[1]
                    count += 1
                    break

                count += 1
            disks.append(disk)

        return disks

    def get_virtual_disk_members(self, vid, num):
        out, err, ret = self.megacli('-LDPDInfo -a%d' % self.adapter)
        count = 0
        pos = 0
        pds = list()
        for line in out.splitlines():
            if 'Virtual Drive:' in line:
                if int(line.split()[2].strip()) == vid:
                    pos = out.splitlines().index(line)
                    break

        for line in out.splitlines()[pos:]:
            if 'Device Id' in line:
                pds.append(int(
                    line.split(':')[1].strip()))
                count += 1
            if count == num:
                break
        return pds

    def get_virtual_disks(self, adapter=0):
        vdisks = list()
        count = 0
        num = self.count_virtual_disks()
        if not num:
            return dict()

        out, err, ret = self.megacli('-LdInfo -Lall -a%d' % adapter)
        for x in range(0, num):
            vd = dict()
            for line in out.splitlines()[count:]:

                if 'Virtual Drive:' in line:
                    vd['id'] = int(line.split(':')[1].split()[0].strip())
                    count += 1
                    continue

                if 'RAID Level' in line:
                    primary = int(line.split(':')[1].split(',')[0].split('-')[1])
                    secondary = int(line.split(':')[1].split(',')[1].split('-')[1])
                    vd['raid_level'] = (primary, secondary)
                    count += 1
                    continue

                if 'Number Of Drives' in line:
                    vd['drive_count'] = int(line.split(':')[1].split()[0].strip())
                    count += 1
                    continue

                if 'Span Depth' in line:
                    vd['span_depth'] = int(line.split(':')[1].split()[0].strip())
                    count += 1
                    break
                count += 1

            phys_ids = self.get_virtual_disk_members(vd.get('id'),
                                                     vd.get('drive_count'))
            vd['phys_ids'] = phys_ids
            vdisks.append(vd)

        return vdisks

    @classmethod
    def quantify_version(cls, version_string):
        major, minor, release = version_string.split('.')
        return int(major), int(minor), release

    @property
    def firmware_version(self):
        version = None
        for line in self.raw_adapter_info:
            if 'FW Package' in line:
                version = line.split(':')[1].strip()
                break
        if not version:
            raise LSIRaidException('Could not determine firmware package version')
        return MegaCLI.quantify_version(version)

    def flash_firmware(self, path):
        if not os.path.exists(path):
            raise LSIRaidException('Firmware blob is to be missing at %s' % path)

        out, err, ret = self.megacli('-adpfwflash -f %s -a%d' % (path, self.adapter))

        if ret:
            raise LSIRaidException('Error applying firmware: %d %s %s' % (ret, out, err))

        return out, err, ret
