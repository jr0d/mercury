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
The current device routing table
"""

from . import inspector
from mercury.inspector.hwlib.iproute2 import IPRoute2


@inspector.expose('routes')
def route_inspector():
    return IPRoute2().table


def find_default_route(routes):
    """

    :param routes:
    :return:
    """
    _defaults = []
    for route in routes:
        if route.get('destination') == 'default':
            if 'metric' not in route:
                route['metric'] = 0
            _defaults.append(route)

    if not _defaults:
        return {}

    return sorted(_defaults, key=lambda _d: int(_d['metric']))[0]


if __name__ == '__main__':
    from pprint import pprint
    table = route_inspector()
    pprint(table)
    pprint('-' * 10)
    pprint(find_default_route(table))
