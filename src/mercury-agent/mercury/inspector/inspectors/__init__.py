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

from .inspector import inspectors, late_inspectors, expose, expose_late

from .cpu import cpu_inspector
from .dmi import dmi_inspector
from .interfaces import interface_inspector
from .os_storage import os_storage_inspector
from .mem import memory_inspector
from .pci import pci_inspector
from .routes import route_inspector

# Late

from .raid import raid_inspector
from .bmc import bmc_inspector