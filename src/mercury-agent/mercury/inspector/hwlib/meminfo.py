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

from size.size import Size


def parse_meminfo():
    with open('/proc/meminfo') as fp:
        data = fp.read()

    d = {}
    for line in data.splitlines():
        line = line.strip()
        if not line:
            continue
        k, v = line.split(':')
        v = v.strip()
        if 'kB'in v:
            v = Size(v).bytes
        d[k] = v

    return d

if __name__ == '__main__':
    print(parse_meminfo())
