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

import os
import logging
import shlex
import subprocess

log = logging.getLogger(__name__)


class CLIResult(str):
    ENCODING = 'utf-8'

    def __new__(cls, *args, **kwargs):
        return str.__new__(cls, object=cls.__decode(args[0]))

    def __init__(self, stdout='', stderr='', returncode=None):
        self._stdout = stdout
        self._stderr = stderr
        self.returncode = returncode

        super(CLIResult, self).__init__()

    @classmethod
    def __decode(cls, v):
        if isinstance(v, bytes):
            return v.decode(cls.ENCODING)
        return v

    def __str__(self):
        return self.__decode(self._stdout)

    def __repr__(self):
        return self.__str__()

    @property
    def stdout(self):
        return self.__str__()

    @property
    def stderr(self):
        return self.__decode(self._stderr)

    @stdout.setter
    def stdout(self, value):
        self._stdout = value

    @stderr.setter
    def stderr(self, value):
        self._stderr = value


class CLIException(Exception):
    """
    Exception used by cli.run function
    """
    pass


def run(command, bufsize=1048567, dry_run=False, raise_exception=False, ignore_error=False,
        quiet=False, env=None, _input=''):
    """Runs a command and stores the important bits in an attribute string.


    :param command: Command to execute.
    :type command: str.
    :param raise_exception:
    :param ignore_error:
    :param env:
    :param quiet:
    :param bufsize: Buffer line size.
    :type bufsize: int.
    :param _input: Pass data into stdin fd

    :param dry_run: Should we perform a dry run of the command.
    :type dry_run: bool.

    :returns: :func:`mercury_CLIResult`.

    """
    if not quiet:
        log.debug('Running: %s' % command)
    our_env = os.environ.copy()
    our_env.update(env or dict())
    cmd = shlex.split(str(command))
    stdin = _input and subprocess.PIPE or None
    if not dry_run:
        p = subprocess.Popen(cmd,
                             stdin=stdin,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             bufsize=bufsize,
                             env=our_env)
        out, err = p.communicate()

        ret = p.returncode
    else:
        out, err, ret = '', '', 0

    if not quiet:
        log.debug('Return Code: %d' % ret)
        if out:
            log.debug('stdout: \n%s' % out.strip())
    if ret and not ignore_error:
        log.error('Return: %d running: %s stdout: %s\nstderr: \n%s' % (ret,
                                                                       command,
                                                                       out.strip(),
                                                                       err.strip()))
        if raise_exception:
            raise CLIException(err)

    cli_result = CLIResult(out, err, ret)

    return cli_result


def find_in_path(filename):
    if os.path.split(filename)[0]:
        _temp_path = os.path.realpath(os.path.expanduser(filename))
        if os.path.exists(_temp_path):
            return _temp_path

    else:
        for path in os.environ['PATH'].split(os.pathsep):
            abspath = os.path.join(path, filename)
            if os.path.exists(abspath):
                return abspath
