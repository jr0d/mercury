import mock
import requests

import mercury.client.base as client_base
from tests.unit import base as test_base


class TestClientBase(test_base.MercuryClientUnitTest):
    
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
