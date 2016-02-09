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

"""
Author: Chad Catlett

HP class using diag method to get full controller details. There is a PR against 
this library that replaces methods using diag, with simple parsing.
"""
import logging
import pexpect  # smh
import os
import re
import time
import zipfile

from xml.etree import ElementTree

from StringIO import StringIO
from subprocess import Popen, PIPE

LOG = logging.getLogger(__name__)


class HPRaidException(Exception):
    pass


class HPRaid(object):
    def __init__(self, hpacucli_bin="/usr/sbin/hpssacli",
                 hpacuscripting_bin="/usr/sbin/hpssascripting"):
        self.hpacucli_bin = hpacucli_bin
        self.hpacuscripting_bin = hpacuscripting_bin
        self.diag_data = self._get_diag()

    @staticmethod
    def _cmd(cmd, args, bufsize=1048567):
        cmd = [cmd] + args.split()
        p = Popen(cmd, stdout=PIPE, stderr=PIPE, bufsize=bufsize)
        out, err = p.communicate()
        ret = p.returncode
        return out, err, ret

    def cli(self, args):
        return self._cmd(self.hpacucli_bin, args)

    def scripting(self, args):
        return self._cmd(self.hpacuscripting_bin, args)

    def dmsetup(self, args):
        return self._cmd("/sbin/dmsetup", args)

    def _get_diag(self):
        self.cli("ctrl all diag file=/tmp/diag.zip")
        z = zipfile.ZipFile("/tmp/diag.zip", "r")
        xml_data = z.read("ADUReport.xml")
        z.close()
        os.unlink("/tmp/diag.zip")
        return ElementTree.parse(StringIO(xml_data))

    def _get_current_array_config(self):
        out, err, ret = self.scripting("-c /tmp/current.xml")
        if ret:
            raise HPRaidException("Failed to get current drive configuration!")
        xml_data = ElementTree.parse("/tmp/current.xml")
        os.unlink("/tmp/current.xml")
        return xml_data

    def get_slot(self):
        xml_data = self.diag_data
        a = xml_data.find(".//Device[@deviceType='ArrayController']/MetaStructure/MetaProperty[@id='PCI Slot']")
        return int(a.attrib['metaValue'])

    def get_physical_drives(self):
        xml_data = self.diag_data
        drives = []
        for i in xml_data.findall(".//Device[@deviceType='PhysicalDrive']"):
            port = i.find(".//MetaProperty[@id='Physical Port']").get("value")
            box = int(i.find(".//MetaProperty[@id='Physical Box']").get("value"), 16)
            bay = int(i.find(".//MetaProperty[@id='Physical Bay']").get("value"), 16)
            block_size = int(i.find(".//MetaProperty[@id='Block Size']").get("value"), 16)
            total_blocks = int(i.find(".//MetaProperty[@id='Total Blocks']").get("value"), 16)
            scsi_id = int(i.find(".//MetaProperty[@id='SCSIID']").get("value"), 16)
            total_bytes = block_size * total_blocks
            gb = total_bytes / (1024.0 ** 3)
            drives.append(dict(port=port, box=box, bay=bay, size=gb, scsi_id=scsi_id))
        return drives

    def get_logical_drives(self):
        xml_data = self._get_current_array_config()

        ld_drives = []
        for i in xml_data.findall(".//Array"):
            drives = i.find("Drive").text
            drives = re.sub(r"(\s|,)+", " ", drives).split()
            raid = i.find(".//Raid").text
            size = i.find(".//Size").text
            array_id = i.get("ID")
            ld_id = i.find("LogicalDrive").get("ID")
            spares = i.find(".//OnlineSpare").text
            if spares.lower() == 'no':
                spares = []
            else:
                spares = re.sub(r"(\s|,)+", " ", spares).split()
            ld_drives.append(dict(
                drives=drives,
                raid=raid,
                size=size,
                array_id=array_id,
                ld_id=ld_id,
                spares=spares
            ))

        return ld_drives

    def get_physical_by_id(self, scsi_id):
        for i in self.get_physical_drives():
            if i['scsi_id'] == scsi_id:
                return i

    def create_ssd_array(self, cmd):
        expect_string = r"""\
Warning: SSD Over Provisioning Optimization will be performed on the physical
\r\n         drives in this array. This process may take a long time and cause this
\r\n         application to appear unresponsive. Continue\? \(y/n\)"""
        cmd_string = "%s %s" % (self.hpacucli_bin, cmd)
        child = pexpect.spawn(cmd_string)
        idx = child.expect([expect_string, pexpect.EOF, pexpect.TIMEOUT])
        if idx == 2:
            child.terminate(True)
            raise Exception("Could not ")
        if idx == 1:
            return child.read(), '', child.exitstatus

        child.sendline("y")
        child.wait()
        return child.read(), '', child.exitstatus

        # TODO: handle non-matching... blow up the world
        # TODO: figure out how to emulate _cmd() return..

    def create_array(self, array):
        ssd_options = ""
        drives = ",".join(["%s:%s:%s" % (i['port'], i['box'], i['bay']) for i in array['drives']])
        spares = ",".join(["%s:%s:%s" % (i['port'], i['box'], i['bay']) for i in array['hot_spares']])

        for i in array['drives']:
            if 'SSD' in i['device_type'].upper():
                ssd_options = "ssdoverprovisioningoptimization=on"

        cmd = "ctrl slot=%s create type=ld drives=%s raid=%s %s" % (
            self.get_slot(), drives, array['level'], ssd_options
        )

        if ssd_options:
            out, err, ret = self.create_ssd_array(cmd)
        else:
            out, err, ret = self.cli(cmd)

        if ret:
            raise HPRaidException("FAILED to create an array! stderr=%s, stdout=%s, array=%s" % (err, out, str(array)))
        LOG.info("Created array %s" % array['array_letter'])
        if spares:
            cmd = "ctrl slot=%s array %s add spares=%s" % (self.get_slot(), array['array_letter'], spares)
            out, err, ret = self.cli(cmd)
            if ret:
                raise HPRaidException("FAILED to set hotspare configuration! stderr=%s, stdout=%s, array=%s" %
                                      (err, out, str(array)))
            LOG.info("Configured array %s's hotspare information" % array['array_letter'])

    def delete_all_arrays(self):
        if not self.get_logical_drives():
            return
        LOG.info("There are arays to be deleted")
        out, err, ret = self.cli("ctrl slot=%s ld all delete forced" % self.get_slot())
        if ret:
            raise HPRaidException("Failed to delete existing raid arrays! stderr: %s, stdout: %s" % (err, out))
        LOG.info("Deleted all arrays from RAID controller")
        LOG.info("Clearing device mapper")
        self.dmsetup("remove_all --force")

    def configure_raid(self, raid_cfg):

        # HP arrays are identified by a letter, A-Z
        array_letters = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')

        # HP logical disks are identified by an ID #, 1+...
        # the ID is unique across the entire controller, not array
        array_numbers = range(1, 27)

        arrays = list()
        global_hotspares = list()

        for array in raid_cfg:
            if array['raid_level'] == -1:
                for phs in array['phy_slot_map']:
                    global_hotspares.append(self.get_physical_by_id(phs))
                continue
            new_array = dict()
            new_array['array_letter'] = array_letters.pop(0)
            new_array['array_number'] = array_numbers.pop(0)
            if array['raid_level'] == 10:
                new_array['level'] = '1+0'
            else:
                new_array['level'] = array['raid_level']
            new_array_drives = list()
            new_array_hotspares = list()
            for phs in array['phy_slot_map']:
                new_array_drives.append(self.get_physical_by_id(phs))

            # let's sort the drives, so that the hot spare(s)
            # are at a predictable location(the end).
            new_array_drives.sort()

            if array['hot_spare']:
                new_array_hotspares.append(new_array_drives.pop())
            new_array_hotspares.sort()
            new_array['drives'] = new_array_drives
            new_array['hot_spares'] = new_array_hotspares
            arrays.append(new_array)

        if global_hotspares:
            for array in arrays:
                # only add hot spares to non-raid 0 arrays
                # and ones without an existing hotspare
                if array['level'] > 0 and not array['hot_spares']:
                    array['hot_spares'].extend(global_hotspares)

        LOG.info("Clearing RAID configuration")
        self.delete_all_arrays()
        time.sleep(10)
        LOG.info("Arrays to configure")
        for array in arrays:
            LOG.info("Array: %s" % array['array_letter'])
            LOG.info("\tLevel: %s" % array['level'])
            LOG.info("\tDrives: %s" % ",".join(["%s:%s:%s" %
                                                (i['port'], i['box'], i['bay']) for i in array['drives']]))
            LOG.info("\tSpares: %s" % ",".join(["%s:%s:%s" %
                                                (i['port'], i['box'], i['bay']) for i in array['hot_spares']]))
            self.create_array(array)
            time.sleep(10)
