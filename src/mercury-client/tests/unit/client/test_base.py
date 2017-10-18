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
"""Module to unit test mercury.client.base"""

import mock
import requests

import mercury.client.base as client_base

from ..base import MercuryClientUnitTest


class TestClientBase(MercuryClientUnitTest):

    def setUp(self):
        super(TestClientBase, self).setUp()
        self.target = 'test_target'
        self.interface_base = client_base.InterfaceBase(self.target)

    def test_init_service_uri(self):
        self.interface_base.SERVICE_URI = 'test_uri'
        self.interface_base.__init__(self.target)
        assert self.interface_base.base_url == 'test_target/test_uri'

    def test_join_endpoint(self):
        test_endpoint_name = '/some_endpoint/'
        result = self.interface_base.join_endpoint('/some_endpoint/')
        self.assertEqual(
                result,
                self.target + '/' + test_endpoint_name.strip('/'))

    def test_append_header_no_extra(self):
        assert (
            self.interface_base.headers == self.interface_base.append_header(
                dict()))

    def test_append_header_extra(self):
        extra_header = {'Some Header': 'Ya Gots Here'}
        self.interface_base.append_header(extra_header)
        assert extra_header.get('Content-type')
        assert extra_header['Content-type'] == 'application/json'

    @mock.patch('mercury.client.base.requests')
    def test_base_get(self, mock_requests):
        response = mock.Mock()
        mock_requests.get = mock.Mock(return_value=response)
        response.raise_for_status = mock.Mock()
        response.json = mock.Mock()

        result = self.interface_base.get()

        mock_requests.get.assert_called_with(
            self.interface_base.join_endpoint(''), params=None,
            headers=self.interface_base.append_header(None))
        response.raise_for_status.assert_called_with()
        response.json.assert_called_with()
        assert result == response.json()

    @mock.patch('mercury.client.base.json')
    @mock.patch('mercury.client.base.requests')
    def test_base_post(self, mock_requests, mock_json):
        response = mock.Mock()
        mock_requests.post = mock.Mock(return_value=response)
        response.raise_for_status = mock.Mock()
        response.json = mock.Mock()

        result = self.interface_base.post()

        mock_requests.post.assert_called_with(
            self.interface_base.join_endpoint(''), params=None,
            data=mock_json.dumps(None),
            headers=self.interface_base.append_header(None))
        response.raise_for_status.assert_called_with()
        response.json.assert_called_with()
        assert result == response.json()

    def test_query_no_projections(self):
        self.interface_base.post = mock.Mock()
        result = self.interface_base.query('<<insert_query_here>>')

        self.interface_base.post.assert_called_with(
            '/query', data={'query': '<<insert_query_here>>'}, params={},
            extra_headers=None)

    def test_query_projections(self):
        self.interface_base.post = mock.Mock()
        result = self.interface_base.query('<<insert_query_here>>',
                                           projection=['some', 'test', 'data'])

        self.interface_base.post.assert_called_with(
            '/query', data={'query': '<<insert_query_here>>'},
            params={'projection': 'some,test,data'}, extra_headers=None)

    def test_check_error(self):
        expected_data = {'response': 'json'}
        expected_code = 404
        expected_return_value = {
            'code': expected_code,
            'data': expected_data,
            'error': True
        }

        @client_base.check_error
        def _check_error_raises_HTTPError():
            mocked_httperror = requests.exceptions.HTTPError("Mocked error.")
            mocked_httperror.response = mock.Mock()
            mocked_httperror.response.status_code = expected_code
            mocked_httperror.response.json.return_value = expected_data
            raise mocked_httperror

        assert _check_error_raises_HTTPError() == expected_return_value

        expected_text = 'hello'

        @client_base.check_error
        def _check_error_raises_ValueError():
            mocked_httperror = requests.exceptions.HTTPError("Mocked error.")
            mocked_httperror.response = mock.Mock()
            mocked_httperror.response.status_code = expected_code
            mocked_httperror.response.json.side_effect = ValueError("Crud.")
            mocked_httperror.response.text = expected_text
            raise mocked_httperror

        expected_return_value['data'] = expected_text

        assert _check_error_raises_ValueError() == expected_return_value
