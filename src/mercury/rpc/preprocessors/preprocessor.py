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


LOG = logging.getLogger(__name__)

instruction_preprocessors = {}


def add_preprocessor(entry, name, description, doc=None):
    LOG.info('Adding preprocessor %s' % name)
    instruction_preprocessors[name] = {
        'name': name,
        'entry': entry,
        'description': description,
        'doc': doc
    }


def preprocessor(name, description):
    def wrap(entry):
        add_preprocessor(entry, name, description, doc=entry.__doc__)
        return entry
    return wrap

