# Copyright 2017 Rackspace
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
"""Module to unit test mercury.common.configuration."""

import os
import mock

import six

import mercury.common.configuration as config
from tests.unit.base import MercuryCommonUnitTest


class MercuryConfigurationUnitTests(MercuryCommonUnitTest):
    """Unit tests for mercury.common.configuration."""
    @mock.patch('mercury.common.configuration.os.path.isfile')
    def test_find_config(self, isfile_mock):
        """Test find_config() function."""
        # This should find it in the last DEFAULT_SEARCH_DIR.
        isfile_return_values = [
            False for _ in range(0, len(config.DEFAULT_SEARCH_DIRS) - 1)]
        isfile_return_values.append(True)
        isfile_mock.side_effect = isfile_return_values
        full_path = config.find_config("test.yaml")
        assert full_path is not None
        assert isinstance(full_path, six.string_types)
        assert full_path == os.path.join(config.DEFAULT_SEARCH_DIRS[-1],
                                         "test.yaml")

        # Shouldn't find a config file.
        isfile_mock.side_effect = [
            False for _ in range(0, len(config.DEFAULT_SEARCH_DIRS))]
        full_path = config.find_config("test.yaml")
        assert full_path is None

    @mock.patch('mercury.common.configuration.open')
    @mock.patch('mercury.common.configuration.yaml.load')
    def test_configuration_from_yaml(self, yaml_load_mock, open_mock):
        """Test configuration_from_yaml() function."""
        fake_config = {'some_config': 'in_a_dict'}
        yaml_load_mock.side_effect = [fake_config]
        assert config.configuration_from_yaml('test_file') == fake_config
        assert open_mock.return_value.__enter__.return_value.read.called

        open_mock.side_effect = IOError("Whoops!")
        assert config.configuration_from_yaml('test_file') == {}

    @mock.patch('mercury.common.configuration.find_config')
    @mock.patch('mercury.common.configuration.configuration_from_yaml')
    def test_get_configuration(self, config_from_yaml_mock, find_config_mock):
        """Test get_configuration() function."""
        # Normal operation.
        fake_filename = "/some/fake/file.yaml"
        fake_config = {'fake_config': 'im_Fake!'}
        find_config_mock.return_value = fake_filename
        config_from_yaml_mock.return_value = fake_config
        result = config.get_configuration(fake_filename)
        assert isinstance(result, dict)
        assert result == fake_config

        # find_config returns None
        find_config_mock.return_value = None
        assert config.get_configuration(fake_filename) == {}
