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
Bare minimum to get system routing information
"""

from mercury.common.helpers import cli


class IPRoute2(object):
    def __init__(self, path='ip'):
        self.ip_path = cli.find_in_path(path)
        self.raw_table = self.get_table()
        self.table = []
        self.parse_table()

    def ip(self, args):
        command = '%s %s' % (self.ip_path, args)
        return cli.run(command)

    @staticmethod
    def _dzip(l):
        _d = {}
        length = len(l)
        if length % 2:
            raise Exception('The list length is ODD, cannot unzip')
        for idx in range(0, len(l), 2):
            _d[l[idx]] = l[idx+1]
        return _d

    def parse_table(self):
        singletons = ['dead', 'onlink', 'pervasive', 'offload', 'notify', 'linkdown']
        for line in self.raw_table.splitlines():
            if line:
                line = line.split()
                route = {'destination': line[0]}
                for singleton in singletons:
                    if singleton in line:
                        route[singleton] = True
                        line.remove(singleton)

                route.update(self._dzip(line[1:]))
                self.table.append(route)

    def get_table(self):
        return self.ip('route show')


if __name__ == '__main__':
    ip_route = IPRoute2()
    from pprint import pprint
    pprint(ip_route.table)
