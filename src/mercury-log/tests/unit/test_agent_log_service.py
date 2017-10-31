import mock
import pytest
import unittest

from mercury.common.exceptions import MercuryClientException
from mercury.log_service import server as log_server

mock_make_agent_log_service = mock.MagicMock()


def mock_init(self, bind_address):
    self.bind_address = bind_address
    self.context = mock.MagicMock()
    self.socket = mock.MagicMock()
    self.bound = False

class AgentLogServiceTestCase(unittest.TestCase):
    def setUp(self):
        with mock.patch(
                'mercury.log_service.server.SimpleRouterReqService.__init__',
                new=mock_init):
            log_collection = mock.Mock()
            self.agent_log_service = log_server.AgentLogService('invalid_bind_url',
                                                                log_collection)

    def test_process(self):
        with pytest.raises(MercuryClientException):
            self.agent_log_service.process({})

        message = {
            'level': 'DEBUG',
            'scope': '__main__',
            'message': 'The cake is a lie',
            'name': 'super_logger',
            'threadName': '_my_awesome-thread'
        }
        self.agent_log_service.log_collection.insert = mock.MagicMock()
        assert self.agent_log_service.process(message) == {'message': 'ok'}
        self.agent_log_service.log_collection.insert.assert_called_once_with(message)

