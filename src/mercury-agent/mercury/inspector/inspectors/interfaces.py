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
import netifaces

from mercury.inspector.inspectors import inspector

from mercury.inspector.hwlib import biosdevname
from mercury.inspector.hwlib.sysfs import NetClass
from mercury.inspector.hwlib.udev import UDevHelper
from mercury.inspector.hwlib import network_interfaces

log = logging.getLogger(__name__)


def get_udev_interface_by_name(interfaces, name):
    for interface in interfaces:
        if interface.get('INTERFACE') == name:
            return interface


def index_gateways(gateways):
    _d = {}
    for gateway in gateways:
        if gateway == 'default':
            continue
        log.debug(gateway)
        _d[gateway[1]] = list()
        _d[gateway[1]].append(dict(list(zip(['gateway_ip', 'interface', 'default'], gateway))))
    return _d


@inspector.expose('interfaces')
def interface_inspector():
    """
    Doc this by providing an example interfaces data structure
    :return: interface data structure
    """
    i = []
    uh = UDevHelper()
    udev_interfaces = uh.get_network_devices()
    interfaces = network_interfaces.list_interfaces()
    gateways = netifaces.gateways()
    log.debug(gateways)

    for interface in interfaces:
        log.debug('Inspecting: {}'.format(interface))
        ndi = NetClass(interface)
        _iface = dict()
        _iface['devname'] = interface
        address = ndi.address
        if not address:
            continue
        _iface['address'] = address
        _iface['carrier'] = ndi.carrier
        log.debug('Interface {} is {}'.format(interface, ndi.carrier and 'up' or 'down'))
        _iface['dev_port'] = ndi.dev_port
        _iface['duplex'] = ndi.duplex
        _iface['speed'] = ndi.speed
        _iface['predictable_names'] = {}
        try:
            _iface['predictable_names']['biosdevname'] = biosdevname.get_name(interface)
        except OSError:
            _iface['predictable_names']['biosdevname'] = None

        udev_interface = get_udev_interface_by_name(udev_interfaces, interface) or dict()
        _iface['predictable_names']['systemd_udev'] = udev_interface.get('ID_NET_NAME_PATH')
        _iface['predictable_names']['systemd_onboard'] = udev_interface.get('ID_NET_NAME_ONBOARD')
        _iface['predictable_names']['systemd_mac'] = udev_interface.get('ID_NET_NAME_MAC')
        _iface['predictable_names']['systemd_slot'] = udev_interface.get('ID_NET_NAME_SLOT')

        if not udev_interface:
            udev_parent = dict()
        else:
            udev_parent = udev_interface.parent or dict()
        _iface['pci_slot'] = udev_parent.get('PCI_SLOT_NAME')
        _iface['model_name'] = udev_parent.get('ID_MODEL_FROM_DATABASE')
        _iface['vendor_name'] = udev_parent.get('ID_VENDOR_FROM_DATABASE')
        _iface['pci_class'] = udev_parent.get('PCI_CLASS')
        _iface['pci_id'] = udev_parent.get('PCI_ID')
        _iface['pci_subsystem_id'] = udev_parent.get('PCI_SUBSYS_ID')
        _iface['driver'] = udev_parent.get('DRIVER')

        # provide per interface routing table
        _iface['address_info'] = network_interfaces.get_ipv4_network_info(interface)

        ipv4_gateways = gateways.get(netifaces.AF_INET, [])
        _iface['ipv4_gateways'] = index_gateways(ipv4_gateways).get(interface)

        _iface['address_info_v6'] = network_interfaces.get_ipv6_network_info(interface)

        ipv6_gateways = gateways.get(netifaces.AF_INET6, [])
        _iface['ipv6_gateways'] = index_gateways(ipv6_gateways).get(interface)

        # TODO: Add gateway information from netifaces.gateways()
        i.append(_iface)

    return i


def get_interface_by_name(interfaces, name):
    """
    Return an interface by it's devname
    :param name: interface devname
    :param interfaces: interfaces dictionary provided by interface_inspector
    :return: interface dictionary
    """
    for interface in interfaces:
        if interface['devname'] == name:
            return interface


if __name__ == '__main__':
    from pprint import pprint
    logging.basicConfig(level=logging.DEBUG)
    pprint(interface_inspector())
