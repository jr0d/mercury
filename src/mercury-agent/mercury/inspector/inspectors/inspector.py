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

import logging
import sys
import traceback

log = logging.getLogger(__name__)

inspectors = []


def expose(name):
    def wrap(f):
        def wrapped_f(*args, **kwargs):
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
        log.debug('Adding runtime inspector %s (%s)' % (f.__name__, name))
        wrapped_f.__name__ = f.__name__
        wrapped_f.__doc__ = f.__doc__
        inspectors.append((name, wrapped_f))
        return wrapped_f
    return wrap
