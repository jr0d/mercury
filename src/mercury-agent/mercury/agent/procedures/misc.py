# Copyright 2015 Jared Rodriguez (jared at blacknode dot net)
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

from __future__ import print_function
import logging

from mercury.agent.capabilities import capability
from mercury.common.helpers.cli import run


log = logging.getLogger(__name__)


@capability('echo', 'Echo something to the console', num_args=1)
def echo(message):
    """
    Echo the dolphin
    :param message: message to Echo
    :return: None
    """
    log.info('Echo: %s' % message)
    return message


@capability('run', 'Run an arbitrary command', num_args=1)
def runner(command, _input=''):
    """
    Run a shell command
    :param command: The shell command to use
    :param _input: Optional data to pass to stdin
    :return:
    """
    log.info('Running: %s' % command)

    r = run('command', ignore_error=True, raise_exception=False, _input=_input)
    return {
        'stdout': r.stdout,
        'stderr': r.stderr,
        'returncode': r.returncode
    }