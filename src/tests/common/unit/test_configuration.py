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
import pytest
import sys

import six

import mercury.common.configuration as config
import mercury.common.exceptions

from tests.common.unit.base import MercuryCommonUnitTest


class MercuryConfigurationUnitTests(MercuryCommonUnitTest):
    """Unit tests for mercury.common.configuration."""

    def setUp(self):
        """ Backup sys.argv """
        self.argv = sys.argv

    def tearDown(self):
        """ Restore sys.argv """
        sys.argv = self.argv

    @mock.patch('mercury.common.configuration.os.path.isfile')
    def test_find_config(self, isfile_mock):
        """Test find_config() function."""
        # This should find it in the last DEFAULT_SEARCH_DIR.
        isfile_return_values = [False] * len(config.DEFAULT_SEARCH_DIRS)
        isfile_return_values.append(True)
        isfile_mock.side_effect = isfile_return_values
        full_path = config.find_config("test.yaml")
        assert full_path is not None
        assert isinstance(full_path, six.string_types)
        assert full_path == os.path.join(config.DEFAULT_SEARCH_DIRS[-1],
                                         "test.yaml")

        isfile_mock.side_effect = None
        isfile_mock.return_value = False
        # Shouldn't find a config file.
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

    @staticmethod
    def test_mercury_configuration_init():
        mc = config.MercuryConfiguration('test', '/tmp/file.yaml')

        sys.argv = ['test']
        mc.add_option('test', '--test', 'TESTVAR', 'test',
                      default='HELLO')
        namespace = mc.scan_options()
        assert namespace.test == 'HELLO'

    @staticmethod
    def test_mercury_configuration_scan_options():
        sys.argv = ['test', '-c', '/tmp/test.yaml']
        patch_path = 'mercury.common.configuration.configuration_from_yaml'
        with mock.patch(patch_path) as mock_load:
            mock_load.return_value = {
                'test_server': {
                    'host': 'test.com',
                    'port': 31137
                },
                'nest1': {
                    'nest2': {
                        'nest3': 'the cake is a lie'
                    }
                }
            }

            new_mc = config.MercuryConfiguration('test', 'test.yaml')
            new_mc.add_option('host', '--host',
                              'HOST',
                              'test_server.host',
                              default='localhost')

            namespace = new_mc.scan_options()

            # From configuration file
            assert namespace.host == 'test.com'

            # From environment variable
            os.environ['HOST'] = 'test2.com'

            namespace = new_mc.scan_options()

            assert namespace.host == 'test2.com'

            # From command line

            sys.argv += ['--host', 'test3.com']

            namespace = new_mc.scan_options()

            assert namespace.host == 'test3.com'

            # Test no configuration
            sys.argv = ['test']
            del os.environ['HOST']
            new_mc.configuration = {}
            namespace = new_mc.scan_options()

            assert namespace.host == 'localhost'

    @staticmethod
    def test_mercury_configuration_type_conversions():
        # List
        sys.argv = ['test']

        new_mc = config.MercuryConfiguration('test', 'test.yaml')

        new_mc.add_option('array', '--array',
                          'ARRAY',
                          'none.none',
                          special_type=list,
                          default=[1,2,3])

        sys.argv += ['--array=element1,element2,element3']

        namespace = new_mc.scan_options()

        assert isinstance(namespace.array, list)
        assert len(namespace.array) == 3
        assert namespace.array[-1] == 'element3'

        # Bool

        new_mc.add_option('bool', '--bool',
                          'BOOL',
                          'none.none',
                          special_type=bool,
                          default=True)

        namespace = new_mc.scan_options()

        assert namespace.bool

        sys.argv += ['--bool=False']

        namespace = new_mc.scan_options()

        assert not namespace.bool

        # Int & Float

        new_mc.add_option('int', '--int', 'INT', 'none.none',
                          special_type=int)
        new_mc.add_option('float', '--float', 'FLOAT', 'none.none',
                          special_type=float)

        sys.argv += ['--int=20', '--float=2.5']

        namespace = new_mc.scan_options()

        assert namespace.int == 20
        assert namespace.float == 2.5

    @staticmethod
    def test_mercury_configuration_auto_format():
        sys.argv = ['test', '-c', '/tmp/test.yaml']
        patch_path = 'mercury.common.configuration.configuration_from_yaml'
        with mock.patch(patch_path) as mock_load:
            mock_load.return_value = {
                'server': {
                    'host': 'test.com',
                    'port': 31137
                },
                'nest1': {
                    'nest2': {
                        'nest3': 'the cake is a lie'
                    }
                }
            }

            new_mc = config.MercuryConfiguration('test', 'test.yaml')
            new_mc.add_option('nest1.nest2.nest3', default='default')

            namespace = new_mc.scan_options()

            assert namespace.nest1.nest2.nest3 == 'the cake is a lie'

            os.environ['NEST1_NEST2_NEST3'] = \
                'Is it ok to drink beer while writing tests?'

            namespace = new_mc.scan_options()

            assert namespace.nest1.nest2.nest3 == \
                'Is it ok to drink beer while writing tests?'

            sys.argv += ['--nest1-nest2-nest3', 'Writing tests is FUN...']

            namespace = new_mc.scan_options()

            assert namespace.nest1.nest2.nest3 == 'Writing tests is FUN...'

    @staticmethod
    def test_required():
        sys.argv = ['test', '-c', '/tmp/test.yaml']
        new_mc = config.MercuryConfiguration('test', 'test.yaml')

        new_mc.add_option('required', required=True)

        with pytest.raises(mercury.common.exceptions.MercuryConfigurationError):
            new_mc.scan_options()
