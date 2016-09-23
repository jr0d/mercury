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

from . import inspector
from mercury.inspector.hwlib.udev import UDevHelper


@inspector.expose('os_storage')
def os_storage_inspector():
    uh = UDevHelper()
    _os_storage = {}
    storage_devices = uh.discover_valid_storage_devices(fc_enabled=True, loop_enabled=False)
    for storage_device in storage_devices:
        _os_storage[storage_device['DEVNAME']] = (dict(list(storage_device.items())))
    return _os_storage


if __name__ == '__main__':
    from pprint import pprint

    pprint(os_storage_inspector())
