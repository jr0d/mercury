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

from mercury.inspector.inspectors import inspectors, late_inspectors
from mercury.hardware.drivers import registered_drivers, set_driver_cache
from mercury.common.mercury_id import generate_mercury_id

# Global storage for device_info it is mostly read only and only overwritten during
# inspector runs

global_device_info = {}


def _collect():
    _c = dict()
    for inspector, f in inspectors:
        _c[inspector] = f()
    return _c


def inspect():
    """
    Runs inspectors and associates collection with a mercury_id
    :return:
    """
    collected = _collect()
    dmi = collected.get('dmi') or {}
    interfaces = collected.get('interfaces') or {}

    collected['mercury_id'] = generate_mercury_id(dmi, interfaces)

    # populate_drivers

    for driver in registered_drivers:
        _wants = driver['class'].wants

        devices = driver['class'].probe(_wants and collected[_wants] or collected)
        if devices:
            set_driver_cache(driver, devices)

    # TODO: Sort RAID drivers based on devices

    for inspector, f in late_inspectors:
        collected[inspector] = f(collected)

    global global_device_info
    global_device_info.update(**collected)

    return global_device_info
