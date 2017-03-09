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
"""Unit tests for mercury.agent.capabilities"""

import mock

from mercury.agent import capabilities


def test_add_capability():
    """Test add_capability()"""
    capabilities.add_capability('c_entry',
                                'c_name',
                                'Capability Description')

    assert 'c_name' in capabilities.runtime_capabilities

    fake_capability = capabilities.runtime_capabilities['c_name']
    assert fake_capability['name'] == 'c_name'
    assert fake_capability['entry'] == 'c_entry'
    assert fake_capability['description'] == 'Capability Description'

    del capabilities.runtime_capabilities['c_name']


@mock.patch('mercury.agent.capabilities.add_capability')
def test_capability(mock_add_capability):
    """Test @capability() decorator"""
    @capabilities.capability('c_name', 'Capability Description', num_args=1)
    def c_entry(x):
        """Return input."""
        return x

    c_entry('foo')

    mock_add_capability.assert_called_once_with(c_entry,
                                                'c_name',
                                                'Capability Description',
                                                num_args=1,
                                                doc="Return input.",
                                                serial=False,
                                                kwarg_names=None,
                                                no_return=False,
                                                dependency_callback=None,
                                                timeout=1800,
                                                task_id_kwargs=False)
