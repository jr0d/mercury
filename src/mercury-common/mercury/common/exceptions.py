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

import sys
import traceback


class MercuryBackendError(Exception):
    pass


class MercuryIdException(Exception):
    pass


class MercuryCritical(Exception):
    pass


def fancy_traceback_format(preamble='Exception info: '):
    exc_type, exc_value, exc_traceback = sys.exc_info()
    path, line, scope, code = traceback.extract_tb(exc_traceback)[-1]
    return '%s (%s : %s): scope=%s, path=%s, line=%d, code=%s' % (preamble,
                                                                  exc_type,
                                                                  exc_value,
                                                                  scope,
                                                                  path,
                                                                  line,
                                                                  code)
