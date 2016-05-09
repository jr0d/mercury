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



from mercury.common.helpers.size import Size
from mercury.inspector.inspectors import expose_late

from mercury.hardware.drivers.hp_raid import SmartArrayDriver
from mercury.hardware.raid.interfaces.lsi.megaraid.megacli import LSIRaid


MEGACLI_PATH = '/usr/local/sbin/megacli'


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

    if device_info['dmi']['sys_vendor'] == 'HP':
        return 'I am a turtle'

    if device_info['dmi']['sys_vendor'] == 'Dell Inc.':
        return 'I am a zombie'

    return 'I am a {}'.format(device_info['dmi']['sys_vendor'])
