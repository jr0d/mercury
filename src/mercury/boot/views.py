# Copyright 2018 Ruben Quinones (ruben.quinones@rackspace.com)
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
from urllib.parse import urlsplit

import pystache


from flask import request, abort, Response
from flask.views import MethodView

from mercury.common.clients.inventory import InventoryClient
from mercury.boot.configuration import get_boot_configuration


log = logging.getLogger(__name__)
configuration = get_boot_configuration()


class BootView(MethodView):
    """
    Boot method view
    """
    def get(self):
        """
        Boot request, transmit the discover script
        :return:
        """

        mercury_boot_url = '://'.join(urlsplit(request.base_url)[:2])

        with open('scripts/discovery.ipxe') as script_file:
            script = pystache.render(script_file.read(), dict(
                mercury_boot_url=mercury_boot_url))

        return Response(script, content_type='text/plain')


class DiscoverView(MethodView):
    """
    Discover method view
    """
    def __init__(self, *args, **kwargs):
        super(DiscoverView, self).__init__(*args, **kwargs)
        inventory_url = configuration.inventory.inventory_router
        self.inventory_client = InventoryClient(inventory_url)

    @staticmethod
    def render_agent_script():
        with open('scripts/agent.ipxe') as fp:
            template = fp.read()

        return pystache.render(template, **configuration)

    @staticmethod
    def plain(message):
        return Response(message, content_type='text/plain')

    def get(self, mac_address):
        """ Attempt to relate a device using the provided mac address """
        result = self.inventory_client.query({
            'interfaces.address': mac_address
        }, projection={
            'boot': 1,
            'mercury_id': 1,
            'dmi': 1
        })

        if result.get('error'):
            abort(500, result)

        message = result['message']

        if not message['total']:
            log.info('New device: {}'.format(mac_address))
            return self.plain(self.render_agent_script())

        if message['total'] > 1:
            log.error('DUPLICATE MAC ADDRESS: {}'.format(mac_address))
            abort(500, 'Duplicate mac addresses in inventory')

        inventory_data = message['items'][0]

        boot_info = inventory_data.get('boot', {})

        if boot_info.get('script'):
            # Dangerous, can potentially leak entire configuration into image
            # if an attacker knows the key names
            return pystache.render(boot_info['script'], dict(
                **inventory_data, **configuration))

        boot_state = boot_info.get('state', 'agent')

        if boot_state == 'local':
            log.info('Booting {} from hard drive'.format(
                inventory_data['mercury_id']))
            return self.plain('#!ipxe\nexit\n')

        elif boot_info == 'rescue':
            log.info('Booting {} to rescue mode'.format(
                inventory_data['mercury_id']
            ))
            return self.plain('Boot rescue iPXE script here')

        log.info('Booting {} to agent'.format(inventory_data['mercury_id']))
        print(request.base_url)
        return self.plain(self.render_agent_script())
