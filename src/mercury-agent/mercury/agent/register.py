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
import time

import msgpack
import zmq

from mercury.agent.config import AGENT_CONFIG_FILE
from mercury.common.configuration import get_configuration
from mercury.common.exceptions import MercuryCritical
from mercury.inspector.inspectors.interfaces import get_interface_by_name
from mercury.inspector.inspectors.routes import find_default_route


log = logging.getLogger(__name__)


def get_dhcp_ip(device_info, method='simple'):
    """
    Get the ip address provided by the DHCP server. Initial operation will use this IP to register with the rpc
     service. Plans are in the works for providing multiple avenues for selecting/generating(ipv6) addresses. Some
     options are:
        Command line argument
        Kernel command line arguments
        Link layer addressing, sans DHCP (48bit, IPV6 only : RFC2373)
    :param device_info: mercury.agent.inspector device_info
    :param method: Possible methods are:
                    simple - Find the interface used for the default route, select this interfaces primary (first)
                    address
                    udhcpc - A mercury_ghost and mercury.agent.inspector construct. The ghost (ephemeral) os that carries
                    the agent and inspector codes contains a script that is called during udhcpc operation. This
                    script will configured the interface as normal. In addition the script will write a file,
                    mercury_dhcp_info.sh, containing DHCP options recieved from the server (including the dhcp_ip).
    :return: ip address
    """
    if method == 'simple':
        routes = device_info['routes']
        interfaces = device_info['interfaces']
        default_route = find_default_route(routes)
        if not default_route:
            raise MercuryCritical('The is no default route defined, cannot use simple method')
        if 'src' in default_route:
            return default_route['src']

        # If the route does not contain a src definition, we take the first address on the 'default' dev
        default_interface = get_interface_by_name(interfaces, default_route['dev']) or dict()
        address_info = default_interface.get('address_info')
        if not address_info:
            raise MercuryCritical('Failed to determine dhcp address')

        log.debug('address_info: %s' % address_info)
        return address_info[0]['addr']


def register(mercury_id, local_ip, local_ip6, capabilities):
    agent_configuration = get_configuration(AGENT_CONFIG_FILE)
    rpc_backend = agent_configuration.get('remote').get('rpc_service')

    if not rpc_backend:
        raise MercuryCritical('Missing rpc backend in local configuration')

    # There is still some confusion regarding how best to determine what ip
    # to publish. Current wisdom suggest that we find the default gateway,
    # determine the interface used for the default route, and take whatever
    # address is configured. This 'should' be the DHCP address right?
    # Relying solely on dhclient (in the initrd) might be an option and would
    # allow for parsing dhclient.leases.
    # Currently, the preboot environment uses udhcpc, so modifying the script
    # udhcpc calls on renew/bound to publish a cookie with vars set by the dhcp
    # server is an option as well

    # Either process should be configurable. ie,
    #  default_ip_source: simple # use default route
    #                     udhcpc # script in preconfig leaves cookie, parse the cookie
    #                     dhclient # parse /var/lib/dhclient.leases

    # And then there is ipv6, where we'd need to DHCP to get a route-able address
    # subnet, and then heuristically generate an ip address in the subnet, forgoing
    # the explicit need for publishing the address
    _caps = capabilities.copy()
    for capability in _caps:
        del _caps[capability]['entry']

    payload = {
        'mercury_id': mercury_id,
        'rpc_address': local_ip,
        'rpc_address6': local_ip6,
        'rpc_port': agent_configuration.get('rpc_port', 9003),
        'ping_port': agent_configuration.get('ping_port', 9004),
        'localtime': time.time(),
        'capabilities': _caps
    }
    packed = msgpack.packb(dict(action='register', client_info=payload))

    ctx = zmq.Context.instance()

    # noinspection PyUnresolvedReferences
    socket = ctx.socket(zmq.REQ)
    socket.connect(rpc_backend)
    socket.send(packed)

    return msgpack.unpackb(socket.recv())


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    from mercury.inspector import inspect
    from mercury.agent.capabilities import runtime_capabilities
    collection = inspect.inspect()

    _mercury_id = collection['mercury_id']
    _local_ip = get_dhcp_ip(collection)
    _local_ip6 = ''

    response = register(_mercury_id, _local_ip, _local_ip6, runtime_capabilities)
