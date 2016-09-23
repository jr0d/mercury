# Copyright 2015 Jared Rodriguez (jared.rodriguez@rackspace.com)
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

import logging
import sys
import traceback

log = logging.getLogger(__name__)

inspectors = []
late_inspectors = []
async_inspectors = []

# TODO: Consider manifest driven inspector orchestration


def run_inspector(name, f, *args, **kwargs):
    # noinspection PyBroadException
    try:
        log.debug('Running inspector: %s' % name)
        return f(*args, **kwargs)
    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        path, line, scope, code = traceback.extract_tb(exc_traceback)[-1]
        log.error('Inspector raised an unhandled exception (%s : %s): name=%s, scope=%s, '
                  'path=%s, line=%d, code=%s' % (exc_type,
                                                 exc_value,
                                                 name,
                                                 scope,
                                                 path,
                                                 line,
                                                 code))
        return None


def expose(name):
    def wrap(f):
        def wrapped_f(*args, **kwargs):
            return run_inspector(name, f, *args, **kwargs)
        log.debug('Adding runtime inspector %s (%s)' % (f.__name__, name))
        wrapped_f.__name__ = f.__name__
        wrapped_f.__doc__ = f.__doc__
        inspectors.append((name, wrapped_f))
        return wrapped_f
    return wrap


def expose_late(name, run_if=None):
    """Hardware dependent inspectors, such as those dependent on OEM/ODM utilities
    :param run_if: callback funtion that takes device_info as an argument. This is optional,
        run_if can always be added by other means
    """
    def wrap(f):
        def wrapped_f(early_device_info):
            if hasattr(f, 'run_if') and not f.run_if(early_device_info):
                log.info('Requirement not satisfied for %s (%s)' % (f.__name__, name))
                return None
            return run_inspector(name, f, early_device_info)
        log.debug('Adding late inspector %s (%s)' % (f.__name__, name))
        wrapped_f.__name__ = f.__name__
        wrapped_f.__doc__ = f.__doc__
        if run_if:
            wrapped_f.run_if = run_if
        late_inspectors.append((name, wrapped_f))
        return wrapped_f
    return wrap
