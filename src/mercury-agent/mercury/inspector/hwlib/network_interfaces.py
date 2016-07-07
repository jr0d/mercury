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
import netifaces


log = logging.getLogger(__name__)


def get_default_interface():
    """
    Get default AF_INET interfaces
    :return: kernel device name
    """
    gws = netifaces.gateways()
    if 'default' not in gws:
        return ''

    route = gws['default'].get(netifaces.AF_INET)
    if route:
        return route[1]


def get_link_addresses(exclude_loopback=True):
    """
    Format a list containing AF_LINK info for each interface
    :param exclude_loopback: Bool
    :return: list of dicts : {'interface': interface_name, 'mac_address': ethernet address}
    """
    interfaces = list_interfaces(exclude_loopback)
    link_info = list()
    for interface in interfaces:
        addresses = netifaces.ifaddresses(interface)
        link_address = addresses.get(netifaces.AF_LINK)
        if link_address:
            link_info.append({'interface': interface, 'mac_address': link_address[0]['addr']})

    return link_info


def get_ipv4_network_info(interface):
    """
    Helper to get only AF_INET addresses, something we are likely to need often. Be aware this function will return a
    list of addresses associated with the interface. The order of the list is unknown and matching networks to routes
    may be required in instances where there are multiple addresses (vlans, aliases, etc). As such, our code should
    check the length of the list even when we assume a length of 1.

    :param interface: device name, eth0, enp3s0, em1, etc.
    :return: A list of ipv4 info dicts {addr, broadcast || peer, netmask}
    """
    if interface not in list_interfaces():
        return []
    addresses = netifaces.ifaddresses(interface)
    return addresses.get(netifaces.AF_INET, [])


def get_ipv6_network_info(interface):
    """
    The same as get_ipv4_network_info but for AF_INET6
    :param interface:
    :return:
    """
    if interface not in list_interfaces():
        return []
    addresses = netifaces.ifaddresses(interface)
    return addresses.get(netifaces.AF_INET6, [])


def get_network_info(interface):
    if interface not in netifaces.interfaces():
        return


def list_interfaces(exclude_loopback=True):
    interfaces = netifaces.interfaces()
    if exclude_loopback:
        interfaces = [i for i in interfaces if i != 'lo']

    return interfaces


def get_gateways():
    return netifaces.gateways()
