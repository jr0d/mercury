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

# https://kallesplayground.wordpress.com/useful-stuff/hp-smart-array-cli-commands-under-esxi/ < This!

"""
Parsing (scraping) this output is dangerous and calls into this class should
be treated with extreme prejudice.

THERE BE DRAGONS HERE
"""

import logging
import os
import re
import time

from mercury.common.helpers.cli import run, find_in_path
from mercury.common.helpers.size import Size

LOG = logging.getLogger(__name__)


class HPRaidException(Exception):
    pass


class HPParserException(Exception):
    pass


def __extract_pci_address(line):
    return line.split()[-1].strip()


def __scrub_label(label):
    label = label.replace('(', '').replace(')', '').strip()
    return label.lower().replace(' ', '_')


def parse_adapter_details(raw_data):
    _adapters = []
    detail_indent = ' ' * 3

    array_details = None
    for l in raw_data.splitlines():
        if not l:
            continue

        if l[:3] != detail_indent:  # ascii space
            LOG.debug('Parsing arry line: %s' % l)
            name, slot = l.split('in Slot')
            array_details = {'name': name.strip()}
            _adapters.append(array_details)
            continue

        else:
            if 'PCI Address' in l:
                array_details['pci_address'] = __extract_pci_address(l)
                continue
            label, data = l.split(':', 1)
            array_details[__scrub_label(label)] = data.strip()

    return _adapters


def __parse_array_line(line):
    line = line.strip()

    array_info = {
        'letter': line.split()[1],
        'type': line.split()[3].strip('(,'),
        'free_space': Size(line.split(':')[1].strip().strip(')'))
    }

    return array_info


def __parse_ld_line(line):
    line = line.strip()
    size, raid_type, status = [x.strip()
                               for x in line.split('(')[1].strip(')').split(',')]
    raid_level = raid_type.split()[1]
    if raid_level == '1+0':
        raid_level = 10
    else:
        raid_level = int(raid_level)

    ld_info = {
        'id': int(line.split()[1]),
        'size': Size(size),
        'level': raid_level,
        'status': status
    }

    return ld_info


def __parse_pd_line(line):
    line = line.strip()
    port, box, bay = line.split()[1].split(':')
    disk_type, size, status = [x.strip()
                               for x in line.split('(')[1].strip(')').split(',')[1:]]
    pd_info = {
        'port': port,
        'box': box,
        'bay': bay,
        'type': disk_type,
        'size': Size(size),
        'status': status
    }

    return pd_info


def parse_show_config(config):
    _drive_indent = ' ' * 6
    _array_indent = ' ' * 3

    array_info = {}
    arrays = []
    unassigned_drives = False
    unassigned = []
    drives = []
    configuration = {'arrays': arrays, 'unassigned': unassigned}

    for line in config.splitlines():
        if line[:6] == _drive_indent:
            pd_info = None
            ld_info = None

            # What are we looking at?

            if 'physicaldrive' in line:
                pd_info = __parse_pd_line(line)
                drives.append(pd_info)
            elif 'logicaldrive' in line:
                ld_info = __parse_ld_line(line)
            else:
                raise HPParserException('Found something other than an ld or pd at indent level 6')

            if array_info:
                if pd_info:
                    array_info['physical_drives'].append(
                        pd_info
                    )

                elif ld_info:
                    array_info['logical_drives'].append(
                        ld_info
                    )

            if unassigned_drives:
                if pd_info:
                    unassigned.append(
                        pd_info
                    )

        if line[:3] == _array_indent:
            if line.find('array') == 3:
                if array_info:
                    arrays.append(array_info)

                array_info = __parse_array_line(line)
                array_info['physical_drives'] = []
                array_info['logical_drives'] = []
                continue

            if line.find('unassigned') == 3:
                arrays.append(array_info)
                array_info = None
                unassigned_drives = True
                continue

    # If there are no unassigned drives, we need to append the last array

    if not unassigned_drives:
        arrays.append(array_info)

    return drives, configuration


def parse_drive_info(pd_info):
    details_indent = ' ' * 9
    pd_details = {}
    for line in pd_info.splitlines():
        if not line:
            continue

        if line.find(details_indent) == 0:
            label, data = line.split(':', 1)
            pd_details[__scrub_label(label)] = data.strip()

    return pd_details


class HPSSA(object):
    details_command = 'ctrl all show detail'
    parity_levels = [5, 6, 50, 60]

    def __init__(self, hpssa_path='hpssacli'):
        self.hpssacli_path = find_in_path(hpssa_path)
        self.adapters = self._raw_system_info()

    def run(self, cmd):
        return run('%s %s' % (self.hpssacli_path, cmd))

    def _get_raw_config(self, slot):
        cmd = 'ctrl slot=%s show config' % slot
        # TODO: TEST TEST TEST, check return and raise
        return self.run(cmd)

    def _raw_system_info(self):
        # TODO: TEST 1, run on system that is missing smart array devices
        # TODO: Check return code and raise an Exception when appropriate
        raw_details = self.run(self.details_command)

        adapters = parse_adapter_details(raw_details)

        for adapter in adapters:
            _config = self._get_raw_config(adapter['slot'])
            adapter['drives'], adapter['configuration'] = parse_show_config(_config)

        return adapters

    def refresh(self):
        self.adapters = self._raw_system_info()

    def get_slot_details(self, slot):
        for adapter in self.adapters:
            # TODO: clean up adapter structure, so that ints are ints, OKs or bools, etc
            if slot == int(adapter['slot']):
                return adapter

    def cache_ok(self, slot):
        adapter = self.get_slot_details(slot)
        return adapter.get('cache_status') == 'OK'

    def get_arrays(self, slot):
        adapter = self.get_slot_details(slot)
        return adapter['configuration']['arrays']

    def get_array_letters(self, slot):
        arrays = self.get_arrays(slot)
        return [x['letter'] for x in arrays]

    def get_next_array_letter(self, slot):
        """
        TODO: Do some research here to determine what happens when we encounter more
        than 26 arrays
        :return:
        """
        letters = self.get_array_letters(slot)
        if not letters:
            return 'A'

        last_letter = letters[-1]
        if 'letter' == 'Z':
            # TODO: Find out an array after Z becomes AA, if not ... *gasp*
            raise HPRaidException('Really dumb limitation encountered')
        return chr(ord(last_letter) + 1)

    def get_array(self, slot, letter):
        arrays = self.get_arrays(slot)
        for array in arrays:
            if array['letter'] == letter:
                return array

    def get_drive(self, slot, drive_id):
        adapter = self.get_slot_details(slot)
        for drive in adapter['drives']:
            _id = '%s:%s:%s' % (drive['port'], drive['box'], drive['bay'])
            if drive_id == _id:
                return drive

    @staticmethod
    def _expand_range(_id_range):
        """
        Ditch this, we should sort drives by port:box:bay and then select drives by
        enum index
        :param _id_range:
        :return:
        """
        expanded = []
        sp = _id_range.split(':')
        loc = sp[:2]
        r = sp[2]

        for i in xrange(*[int(x) for x in r.split('-')]):
            expanded.append('%s:%d' % (loc, i))

        return expanded

    def get_drives_from_selection(self, slot, s):
        adapter = self.get_slot_details(slot)
        if not adapter:
            return []

        if s == 'all':
            return adapter['drives']

        if s == 'allunassigned':
            return adapter['configuration']['unassigned']

        items = s.split(',')

        drives = []
        for idx in xrange(len(items)):
            if '-' in items[idx]:
                drives += self._expand_range(items[idx])
                continue
            drives.append(self.get_drive(slot, items[idx]))

        return drives

    @staticmethod
    def is_ssd(drive):
        return 'Solid State' in drive['type'] or 'SSD' in drive['type']

    def all_ssd(self, drives):
        for drive in drives:
            if not self.is_ssd(drive):
                return False
        return True

    def create(self, slot, selection, raid, array_letter=None, array_type='ld', size='max',
               stripe_size='default', write_policy='writeback',
               secotors=32, caching=True, data_ld=None,
               parity_init_method='default'):
        """
        Create an array

        :param selction: all, allunassigned, Port:Box:Bay,...  , 1I:1:1-1I:1:6
        :param raid: 0, 1, 5, 6, 1+0, 1+0asm, 50, 60
        :param array_type: ld, ldcache, arrayr0
        :param size: size in MB, min, max, maxmbr
        :param stripe_size: 2**3-10 (8-1024), default
        :param write_policy:
        :param secotors: 32, 64
        :param caching: True | False
        :param data_ld: ld ID, required if array_type == ldcache
        :return:
        """

        if not array_letter:
            array_letter = self.get_next_array_letter(slot)

        command = 'ctrl slot={slot} create type={type} drives={drives} ' \
                  'raid={raid} size={size} stripesize={stripe_size}'.format(
            **{
                'slot': slot,
                'type': array_type,
                'drives': selection,
                'raid': raid,
                'size': size,
                'stripe_size': stripe_size
            }
        )

        standard_array_options = {
            'sectors': secotors,
            'caching': caching and 'enable' or 'disable',
        }

        cache_array_options = {
            'datald': data_ld,
            'writepolicy': write_policy
        }

        ssd_array_options = {
            'ssdoverprovisioningoptimization': 'on'
        }

        parity_array_options = {
            'parityinitializationmethod': parity_init_method
        }

        build_options = lambda o: ' %s' % ' '.join(['%s=%s' % (x, o[x]) for x in o])

        standard_array_types = ['ld', 'arrayr0']

        if array_type in standard_array_types:
            command += build_options(standard_array_options)

        elif array_type == 'ldcache':
            if not data_ld:
                raise HPRaidException('Type: ldcache requires data_ld')

            command += build_options(cache_array_options)

        else:
            raise HPRaidException('Type: %s is not supported' % array_type)

        if self.all_ssd(self.get_drives_from_selection(slot, selection)):
            command += build_options(ssd_array_options)

        try:
            if int(raid) in self.parity_levels:
                command += build_options(parity_array_options)
        except ValueError:
            # 1+0 and 1+0asm will hit here
            pass

        result = self.run(command)

        # return array_letter
        LOG.info(array_letter)
        return result

    def get_pd_info(self, slot, pd):
        cmd = 'ctrl slot=%s pd %s show detail' % (slot, pd)
        return parse_drive_info(self.run(cmd))

    @staticmethod
    def assemble_id(pd_info):
        return '%s:%s:%s' % (pd_info['port'], pd_info['box'], pd_info['bay'])

    def get_pd_by_index(self, slot, idx):
        adapter = self.get_slot_details(slot)
        pd_info = adapter['drives'][idx]
        return self.assemble_id(pd_info)
