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

import logging

from mercury.hardware.drivers import get_subsystem_drivers
from mercury.inspector.inspectors import expose_late


log = logging.getLogger(__name__)


# noinspection PyUnusedLocal
@expose_late('raid')
def raid_inspector(device_info):
    drivers = get_subsystem_drivers('raid')

    if not drivers:
        return

    _inspected = list()

    for driver in drivers:
        log.info('Running RAID inspector %s' % driver.name)
        data = driver.inspect()
        if isinstance(data, list):
            _inspected += data
        else:
            _inspected.append(data)

    return _inspected
