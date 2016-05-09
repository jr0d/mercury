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

from mercury.inspector.inspectors import inspectors, late_inspectors
from mercury.hardware.drivers import driver_pci_map, registered_drivers
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

    for driver_type in registered_drivers:
        for driver in registered_drivers['driver_type']:
            pci_ids = driver.probe()
    for inspector, f in late_inspectors:
        collected[inspector] = f(collected)

    global global_device_info
    global_device_info.update(**collected)

    return global_device_info
