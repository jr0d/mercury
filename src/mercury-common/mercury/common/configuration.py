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
import os
import yaml

LOG = logging.getLogger(__name__)

default_search_dirs = ['.', '~/.mercury', '/etc/mercury']


def find_config(f, dirs=None):
    dirs = dirs or list() + default_search_dirs
    for directory in dirs:
        full_path = os.path.join(os.path.expanduser(directory), f)
        if os.path.isfile(full_path):
            return full_path


def configuration_from_yaml(path):
    with open(path) as fp:
        return yaml.load(fp.read())


def get_configuration(filename):
    config_file = find_config(filename)
    if not config_file:
        LOG.warning('%s not found' % filename)
        return {}
    return configuration_from_yaml(config_file)
