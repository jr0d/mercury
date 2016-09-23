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

from press.layout.size import Size


class HPParserException(Exception):
    pass


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
