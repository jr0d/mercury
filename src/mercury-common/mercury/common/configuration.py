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
"""Provides YAML configuration loading functionality for mercury."""

import logging
import os
import yaml


LOG = logging.getLogger(__name__)


DEFAULT_SEARCH_DIRS = ['.', '~/.mercury', '/etc/mercury']


def find_config(filename, dirs=None):
    """Searches for configuration files. Setting the environment variable:
        ```
            MERCURY_SEARCH_DIRS
        ```
        can be used to extend the search paths as well

    :param filename: The configuration file path or a filename to search for
    :param dirs: A list of filesystem directories to search for the
        configuration file. Parameter defaults to None, which means a set
        of default locations will be searched.
    :returns: string or None -- The full path of the configuration file if
        found.  None otherwise.
    """
    if os.path.isfile(filename):
        return filename

    dirs = dirs or list() + DEFAULT_SEARCH_DIRS
    if 'MERCURY_SEARCH_DIRS' in os.environ:
        dirs = dirs + os.environ.get('MERCURY_SEARCH_DIRS')

    for directory in dirs:
        full_path = os.path.join(os.path.expanduser(directory), filename)
        if os.path.isfile(full_path):
            return full_path


def configuration_from_yaml(filename):
    """Loads a YAML configuration file.

    :param filename: The filename of the file to load.
    :returns: dict -- A dictionary representing the YAML configuration file
        loaded. If the file can't be loaded, then the empty dict is returned.
    """
    try:
        with open(filename) as infile:
            return yaml.load(infile.read())
    except IOError:
        return {}


def get_configuration(filename):
    """Gets and returns the contents of the configuration file as a dict.

    :param filename: The filename of the configuration file to load.
    :returns: dict -- A dictionary representing the YAML configuration file
        loaded. If the file was not found or loaded, then returns an empty
        dict.
    """
    config_file = find_config(filename)
    if not config_file:
        LOG.warning('%s not found' % filename)
        return {}
    return configuration_from_yaml(config_file)
