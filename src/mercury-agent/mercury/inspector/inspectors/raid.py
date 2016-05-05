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

from collections import OrderedDict

from mercury.hardware.raid.interfaces.hpsa.hpacu import HPRaid

from mercury.common.helpers.size import Size
from mercury.inspector.inspectors import expose_late
from mercury.hardware.raid.interfaces.lsi.megaraid.megacli import LSIRaid


MEGACLI_PATH = '/usr/local/sbin/megacli'


class HPRaidCollector(dict):
    @staticmethod
    def sort_disks(disks):
        box_index = OrderedDict()

        for _d in sorted(disks, key=lambda k: k['box']):
            box = _d['box']
            if box not in box_index:
                box_index[box] = [_d]
            else:
                box_index[box].append(_d)

        for idx in box_index:
            box_index[idx].sort(key=lambda k: k['bay'])

        # transform statement requires a copy due to lazy indexing
        # possible efficency gain in performing a left(box) right(bay) sort
        disks_sorted = []

        for idx in box_index:
            disks_sorted += box_index[idx]

        return disks_sorted

    def inspect(self):
        hp_raid = HPRaid()
        self['disks'] = list()

        disks = self.sort_disks(hp_raid.get_physical_drives())

        for drive in disks:
            d = {
                'size': drive['size'] * 1024 ** 3,
                'hp_extra': {
                    'scsi_id': drive['scsi_id'],
                    'port': drive['port'],
                    'bay': drive['bay'],
                    'box': drive['box']
                }
            }
            self['disks'].append(d)


class LSIRAIDCollector(dict):
    def inspect(self):
        lsi_raid = LSIRaid(megacli_bin=MEGACLI_PATH)
        self['disks'] = list()
        drives = lsi_raid.pdisks
        for drive in drives:
            d = {
                'size': Size(str(drive['size']) + drive['multiple'], force_iec_values=True).bytes,
                'lsi_extra': {
                    'media_errors': drive['media_errors'],
                    'other_errors': drive['other_errors'],
                    'predictive_errors': drive['predictive_errors'],
                    'slot_number': drive['slot_number'],
                    'state': drive['state']
                }
            }
            self['disks'].append(d)


@expose_late('raid')
def raid_inspector(device_info):
    return 'I am a turtle'
