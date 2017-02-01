import mock
import os

from mercury.common.helpers.cli import CLIResult
from mercury.hardware.raid.interfaces.megaraid import storcli

from ..base import MercuryAgentUnitTest


class StorcliTest(MercuryAgentUnitTest):
    @mock.patch('mercury.common.helpers.cli.run')
    def test_run(self, mock_run):
        mock_run.return_value = CLIResult('', '', 0)

        s = storcli.Storcli()
        assert s.run('') == ''

        mock_run.return_value = CLIResult('Error', '', 1)

        self.assertRaises(storcli.StorcliException, s.run, *('', ))

    @mock.patch('mercury.common.helpers.cli.run')
    def test_run_json(self, mock_run):
        with open(os.path.join(os.path.dirname(__file__),
                               '../resources/storcli.json')) as fp:
            json_data = fp.read()

        mock_run.return_value = CLIResult(json_data, '', 0)

        s = storcli.Storcli()
        assert isinstance(s.run_json('/call show all'), dict)

        mock_run.return_value = CLIResult('not_valid_json', '', 0)

        self.assertRaises(storcli.StorcliException, s.run_json, *('', ))

    @mock.patch('mercury.common.helpers.cli.run')
    def test_controllers(self, mock_run):
        with open(os.path.join(os.path.dirname(__file__),
                               '../resources/storcli.json')) as fp:
            json_data = fp.read()

        mock_run.return_value = CLIResult(json_data, '', 0)

        s = storcli.Storcli()
        assert isinstance(s.controllers, list)

        mock_run.return_value = CLIResult('{}', '', 0)

        def _wrapper():
            return s.controllers

        self.assertRaises(storcli.StorcliException, _wrapper)

    @mock.patch('mercury.common.helpers.cli.run')
    def test_delete(self, mock_run):
        mock_run.return_value = CLIResult('', '', 0)
        s = storcli.Storcli()
        assert s.delete(0) == ''

    @mock.patch('mercury.common.helpers.cli.run')
    def test_add(self, mock_run):
        mock_run.return_value = CLIResult('', '', 0)

        s = storcli.Storcli()
        assert s.add(0, 'r0', '32:0-1') == ''
        assert s.add(0, 'r10', '32:0-3', pdperarray=2) == ''

        self.assertRaises(storcli.StorcliException, s.add, *(0, 'r10', '32:0-3'))

        with open(os.path.join(os.path.dirname(__file__), '../resources/storcli_err.txt')) as fp:
            error_data = fp.read()

        mock_run.return_value = CLIResult(error_data, '', 0)

        self.assertRaises(storcli.StorcliException, s.add, *(0, '', ''))
