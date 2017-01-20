import mock

import mercury.tests.unit.base as test_base
import mercury.client.base as client_base

class TestClientBase(test_base.MercuryClientUnitTest):
    def setUp(self):
        super(TestClientBase, self).setUp()
        self.target = 'test_target'
        self.interface_base = client_base.InterfaceBase(self.target)

    def test_join_endpoint(self):
        test_endpoint_name = '/some_endpoint/'
        result = self.interface_base.join_endpoint('/some_endpoint/')
        self.assertEqual(
                result,
                self.target + '/' + test_endpoint_name.strip('/'))
