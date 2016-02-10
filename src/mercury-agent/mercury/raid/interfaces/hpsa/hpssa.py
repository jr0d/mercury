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
hpssa hierarchy:

slot:
    array:
        logicaldrive:
            physicaldrive

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
    drives = []
    configuration = {'arrays': arrays, 'drives': drives}

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
                continue

    return configuration


class HPSSA(object):
    details_command = 'ctrl all show detail'

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
            adapter['configuration'] = parse_show_config(_config)

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

    def create(self, slot, selection, raid, array_letter=None, array_type='ld', size='max',
               stripe_size='default', write_policy='writeback',
               secotors=32, caching=True, ssd_overprovisioning=False, data_ld=None,
               parity_init_method='default'):
        """
        Create an array

        :param selction: all, allunassigned, Port:Box:Bay,...  , 1I:1:1-1I:1:6
        :param raid: 0, 1, 5, 6, 1+0, 1+0asm, 50, 60
        :param array_type: ld, ldcache, arrayr0
        :param size: size in MB, min, max, maxmbr
        :param stripe_size: 2**3-10 (8-1024), default
        :param secotors: 32, 64
        :param caching: True | False
        :param ssd_overprovisioning: True | False
        :param data_ld: ld ID, required if array_type == ldcache
        :return:
        """
        if array_type == 'ldcache':
            if not data_ld:
                raise HPRaidException('Type: ldcache requires data_ld')
            if caching:
                LOG.warning('Standard caching is not supported on type: ldcache')
                caching = False

        if not array_letter:
            array_letter = self.get_next_array_letter(slot)

        command_builder = 'ctrl slot={slot} array {array_letter} ' \
                          'create type={array_type}'



if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    _hpssa = HPSSA()
    from pprint import pprint
    pprint(_hpssa.adapters)
    print _hpssa.cache_ok(0)




