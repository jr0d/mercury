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
    """Parses IPRoute2 information to allow easy programmatic access."""
    def __init__(self, path='ip'):
        """Inspects the ip routing table and stores it for easy access.

        :parameter path: A string representing the full path (including the
            binary/executable name of the `ip` command. Defaults to `ip`.

        :raises Exception: if the output of ip appears to be malformed.
        """
        self._ip_path = cli.find_in_path(path)
        self._raw_table = self._get_table()
        self._table = []
        self._parse_table()

    def _get_table(self):
        return self.ip('route show')

    @staticmethod
    def _dzip(l):
        _d = {}
        length = len(l)
        if length % 2:
            raise Exception('Unexpected output from `ip route` command: %s' %
                            ' '.join(l))
        for idx in range(0, len(l), 2):
            _d[l[idx]] = l[idx+1]
        return _d

    def _parse_table(self):
        singletons = ['dead', 'onlink', 'pervasive', 'offload', 'notify',
                      'linkdown']
        for line in self._raw_table.splitlines():
            if line:
                line = line.split()
                route = {'destination': line[0]}
                for singleton in singletons:
                    if singleton in line:
                        route[singleton] = True
                        line.remove(singleton)

                route.update(self._dzip(line[1:]))
                self._table.append(route)

    def ip(self, args):
        """Runs the `ip` command with the supplied args and returns the result.

        :parameter args: A string representing the arguments to pass to the
            `ip` command.
        """
        command = '%s %s' % (self._ip_path, args)
        return cli.run(command)

    @property
    def table(self):
        """Gets the ip route table stored by this object.

        :returns: A dict containing the routing table returned by
            `ip route show`.
        """
        return self._table
