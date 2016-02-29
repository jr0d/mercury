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


@capability('exec_press', description='Execute press using the supplied configuration', serial=True,
            kwarg_names=['configuration'])
def execute_press(configuration=None):
        # Make entry main return something
        # TODO: Do not rely on entry_main. Import Press, setup logging, and init plugins here
    return entry_main(configuration)


@capability('exec_press_no_return', description='Execute press using the supplied configuration', serial=True,
            kwarg_names=['configuration'], no_return=True)
def execute_press_nor(configuration=None):
        # TODO: Do not rely on entry_main. Import Press, setup logging, and init plugins here
    return entry_main(configuration)
