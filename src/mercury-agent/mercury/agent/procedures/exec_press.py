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

from mercury.agent.capabilities import capability

from press.entry import entry_main
from press.exceptions import PressCriticalException


@capability('exec_press', description='Execute press using the supplied configuration', serial=True,
            kwarg_names=['configuration'])
def execute_press(configuration=None):
    try:
        # Make entry main return something
        # Modify press to allow injecting a specific log configuration
        # Or.. just rely on the press logging facility?
        # since this is a long operation.. investigate return queue
        # implement serial locking
        # Let's take the time to implement this fully... NMP (no more prototypes)
        entry_main(configuration)
    except PressCriticalException:
        pass

