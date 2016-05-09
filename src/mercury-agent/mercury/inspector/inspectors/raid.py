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

import logging

from mercury.hardware import platform_detection
from mercury.hardware.drivers import registered_drivers
from mercury.inspector.inspectors import expose_late


log = logging.getLogger(__name__)

MEGACLI_PATH = '/usr/local/sbin/megacli'


@expose_late('raid')
def raid_inspector(device_info):
    controller_pci_info = platform_detection.get_raid_controllers(device_info['pci'])

    if not controller_pci_info:
        log.debug('No RAID bus controllers detected')
        return



