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

import pystache
import yaml

from mercury.common.exceptions import MercuryUserError
from mercury.rpc.preprocessors import preprocessor


@preprocessor.preprocessor('press_static_assets', 'Uses user supplied assets to render press configuration templates')
def press_static_assets(target, instruction):
    """Uses a mercury_id indexed asset store which is supplied, in it's entirety, within the instruction
    :param target: A target containing a mercury_id
    :param instruction: A dictionary containing two fields, template and assets
        template is a string containing a mustache formatted press configuration
        assets is a dictionary indexed by mercury_id. Each value contains render information
        relevant to the template. If the asset data does not contain data for the target mercury_id
        a MercuryUserException exception is raised

        Note, this is throw away code. The mercury_assets service will take over the functionality provided
        herein.
    :return: exec_press capability contract
    """

    template = instruction.get('template')
    asset_db = instruction.get('assets')

    if not template and asset_db:
        raise MercuryUserError('Contract is incomplete')

    render_data = asset_db.get(target['mercury_id'])

    if not render_data:
        raise MercuryUserError('Assets supplied do not cover target')

    configuration = pystache.render(template, **render_data)

    return {'method': 'exec_press', 'kwargs': {'configuration': configuration}}