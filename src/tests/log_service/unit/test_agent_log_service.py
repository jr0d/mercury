import mock
import pytest
import unittest

from mercury.common.exceptions import MercuryClientException
from mercury.log_service import service as log_server

mock_make_agent_log_service = mock.MagicMock()


def mock_init(self, bind_address):
    self.bind_address = bind_address
    self.context = mock.MagicMock()
    self.socket = mock.MagicMock()
    self.bound = False

class AgentLogServiceTestCase(unittest.TestCase):
    def setUp(self):
        with mock.patch(
                'mercury.log_service.service.SimpleRouterReqService.__init__',
                new=mock_init):
            log_collection = mock.Mock()
            self.agent_log_service = log_server.AgentLogService('invalid_bind_url',
                                                                log_collection)

    def test_process(self):
        with pytest.raises(MercuryClientException):
            self.agent_log_service.process({})

        message = {
            "name": "mercury.agent.agent",
            "msg": "Injection completed",
            "args": [],
            "levelname": "INFO",
            "levelno": 20,
            "pathname": "/src/mercury/agent/mercury/agent/agent.py",
            "filename": "agent.py",
            "module": "agent",
            "exc_info": None,
            "exc_text": None,
            "stack_info": None,
            "lineno": 89,
            "funcName": "run",
            "created": 1510076870.9318643,
            "msecs": 931.8642616271973,
            "relativeCreated": 405.81798553466797,
            "thread": 139861930071808,
            "threadName": "MainThread",
            "processName": "MainProcess",
            "process": 71,
            "message": "Injection completed",
            "asctime": "2017-11-07 17:47:50,931",
            "mercury_id": "0112426690c16b0fd4586e91731a0cc4f3f918c5af"
        }
        self.agent_log_service.log_collection.insert = mock.MagicMock()
        assert self.agent_log_service.process(message) == {'message': 'ok', 'error': False}
        self.agent_log_service.log_collection.insert.assert_called_once_with(message)

