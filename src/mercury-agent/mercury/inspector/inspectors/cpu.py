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

from . import inspector
from mercury.common.misc.cpuinfo import CPUInfo


@inspector.expose('cpu')
def cpu_inspector():
    _cpu = {}
    cpu_info = CPUInfo()

    processors = cpu_info.physical_index
    for _id in processors:
        processor = processors[_id][0]
        _proc_dict = dict()
        _proc_dict['physical_id'] = _id
        _proc_dict['cores'] = int(processor['cpu_cores'])
        _proc_dict['threads'] = int(processor['siblings'])
        _proc_dict['model_name'] = processor['model_name']
        _proc_dict['cache_size'] = processor['cache_size']
        _proc_dict['cache_alignment'] = int(processor['cache_alignment'])
        _proc_dict['flags'] = processor['flags'].split()
        # speed
        _proc_dict['frequency'] = CPUInfo.get_speed_info(processor)

        _cpu['cpu%d' % _id] = _proc_dict

    return _cpu

if __name__ == '__main__':
    from pprint import pprint

    pprint(cpu_inspector())
