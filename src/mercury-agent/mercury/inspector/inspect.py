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

from mercury.inspector.inspectors import inspectors
from mercury.common.mercury_id import generate_mercury_id


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

    return collected

