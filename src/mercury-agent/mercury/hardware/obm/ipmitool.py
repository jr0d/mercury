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


"""Classes for side channel configuration of various out of band management
controllers

Classes should provide:
    Verify networking configuration
    Create network configuration
    Create/enable default obm user
"""

import logging
import os

from lxml import etree

from mercury.common.helpers import cli

log = logging.getLogger(__name__)

DEFAULT_IPMITOOL_PATH = 'ipmitool'


def get_bmc_handler(vendor, **kwargs):
    _SELECTOR = {
        'Dell Inc.': IPMIToolDrac,
        'Quanta': DCMITool,
        'HP': IPMIToolHP
    }

    handler = _SELECTOR.get(vendor)
    if not handler:
        return
    return handler(**kwargs)


class BMCException(Exception):
    pass


class IPMIToolParsingError(Exception):
    pass


class IPMITool(object):
    def __init__(self, ipmitool_path=DEFAULT_IPMITOOL_PATH):
        self.ipmitool_path = cli.find_in_path(ipmitool_path)

        if not self.ipmitool_path:
            raise OSError("%s does not exist" % ipmitool_path)

        self.net_info = {}
        self.parse_network_info()

    @staticmethod
    def __lan_set(channel, what, value):
        return 'lan set %d %s %s' % (channel, what, value)

    @staticmethod
    def __raw_command(cmd):
        return 'raw %s' % cmd

    def run(self, args, bufsize=1048567, raise_on_error=True, ignore_error=False):
        cmd = self.ipmitool_path + ' ' + args
        return cli.run(cmd, bufsize=bufsize, raise_exception=raise_on_error, ignore_error=ignore_error)

    def parse_network_info(self, channel=1):
        log.debug('Parsing and storing IPMI LAN info')
        args = 'lan print %d' % channel
        out = self.run(args)
        for line in out.splitlines():
            label = line.split(':')[0].strip()
            data = line.split(':')[1].strip()
            if not label:
                continue
            if label == 'IP Address Source':
                self.net_info['source'] = 'Static' in data and 'static' or 'dhcp'
                continue
            if label == 'IP Address':
                self.net_info['ip_address'] = data
                continue
            if label == 'Subnet Mask':
                self.net_info['netmask'] = data
                continue
            if label == 'MAC Address':
                self.net_info['mac_address'] = ':'.join(line.split(':')[1:]).strip()
                continue
            if label == 'Default Gateway IP':
                self.net_info['gateway'] = data
                continue

    def verify_network_info(self, ip_address, netmask, gateway, source):
        if not self.net_info.get('ip_address') == ip_address:
            log.debug('IP: %s != %s' % (ip_address, self.net_info.get('ip_address')))
            return False

        if not self.net_info.get('netmask') == netmask:
            log.debug('NETMASK: %s != %s' % (netmask, self.net_info.get('netmask')))
            return False

        if 'gateway' in self.net_info:
            #  DCMITool does not expose default gateway
            if not self.net_info['gateway'] == gateway:
                log.debug('GATEWAY: %s != %s' % (gateway, self.net_info['gateway']))
                return False

        if not self.net_info.get('source') == source:
            log.debug('SOURCE: %s != %s' % (source, self.net_info.get('source')))
            return False

        return True

    def set_static(self, channel=1):
        self.run(self.__lan_set(channel, 'ipsrc', 'static'))

    def set_dhcp(self, channel=1):
        self.run(self.__lan_set(channel, 'ipsrc', 'dhcp'))

    def configure_static_network(self, ip_address, netmask, gateway, channel=1):
        self.set_static(channel)
        self.run(self.__lan_set(channel, 'ipaddr', ip_address))
        self.run(self.__lan_set(channel, 'netmask', netmask))
        self.run(self.__lan_set(channel, 'defgw', gateway))
        self.parse_network_info()

    def reset_mc_cold(self):
        self.run('mc reset cold')

    def create_superuser(self, username, password, channels=(1, 2), user_id=2):
        self.run('user set name %d %s' % (user_id, username))
        self.run('user set password %d %s' % (user_id, password))
        for channel in channels:
            self.run(
                'channel setaccess %d %d link=on ipmi=on callin=on privilege=4' % (channel,
                                                                                   user_id))
            self.run('sol payload enable %d %d' % (channel, user_id))
        self.run('user enable %d' % user_id)

    @staticmethod
    def parse_output_type1(data):
        key = None
        parsed = {}
        for line in data.splitlines():
            sline = line.split(':', 1)
            if len(sline) == 1:
                if not key:
                    raise IPMIToolParsingError('Key is not set for presumed list value')
                value = sline[0].strip()
                parsed[key].append(value)
                continue
            key = sline[0].strip().lower().replace(' ', '_')
            if not sline[1].strip():
                parsed[key] = list()
            else:
                parsed[key] = sline[1].strip()

        return parsed

    @property
    def bmc_info(self):
        log.debug('Getting bmc info')
        out = self.run('mc info', raise_on_error=False)
        if out.returncode:
            log.error('Problem getting bmc info : '
                      'std {} - err {} - return {}'.format(out, out.stderr, out.returncode))
            return None

        return self.parse_output_type1(out)


class DCMITool(IPMITool):
    def __init__(self, dcmitool_path='/usr/local/sbin/Qdcmitool'):
        self.dcmitool_path = cli.find_in_path(dcmitool_path)
        super(DCMITool, self).__init__(ipmitool_path=dcmitool_path)

    def bootstrap_obm_static(self, ip_address, netmask, gateway, username, password):
        self.configure_static_network(ip_address, netmask, gateway)
        self.create_superuser(username, password, channels=[1])
        return self.verify_network_info(ip_address, netmask, gateway, 'static')


class IPMIToolDrac(IPMITool):
    def __init__(self, ipmitool_path=DEFAULT_IPMITOOL_PATH):
        super(IPMIToolDrac, self).__init__(ipmitool_path=ipmitool_path)
        self.drac_version = self.get_drac_version()

    def get_drac_version(self):
        out = self.run('sdr elist mcloc', raise_on_error=False)
        if not out.returncode:
            return
        try:
            sensors = [i.split('  ', 1)[0] for i in out]
            version = [i for i in sensors if 'DRAC' in i][0]
        except IndexError:
            return
        return version

    def disable_default_password_prompt(self):
        command = '0x30 0xd0 0x00 0x0a 0x08 0x00 0x00 0x00 0x08 0x00 0x00 0x00 0x00 0x00 0x00 0x00'
        if self.drac_version == 'iDRAC7':
            self.run(self.__raw_command(command))

    def bootstrap_obm_static(self, ip_address, netmask, gateway, username, password):
        self.configure_static_network(ip_address, netmask, gateway)
        self.create_superuser(username, password, user_id=2)
        return self.verify_network_info(ip_address, netmask, gateway, 'static')


class IPMIToolHP(IPMITool):
    def __init__(self,
                 ipmitool_path=DEFAULT_IPMITOOL_PATH,
                 hponcfg_path='/sbin/hponcfg',
                 list_users_path='hpxml/list_users.xml',
                 users_path='hpxml/users.xml',
                 add_user_path='hpxml/add_user.xml',
                 del_user_path='hpxml/del_user.xml'):
        super(IPMIToolHP, self).__init__(ipmitool_path=ipmitool_path)

        script_path = os.path.dirname(__file__)

        def _join(p):
            return os.path.abspath(p) and p or os.path.join(script_path, p)

        self.hponcfg_path = _join(hponcfg_path)
        self.list_users_path = _join(list_users_path)
        self.users_path = _join(users_path)
        self.add_user_path = _join(add_user_path)
        self.del_user_path = _join(del_user_path)

    def configure_static_network(self, ip_address, netmask, gateway, channel=2):
        """
        Default channel is different
        :param ip_address:
        :param netmask:
        :param gateway:
        :param channel:
        :return:
        """
        return super(IPMIToolHP, self).configure_static_network(
            ip_address, netmask, gateway, channel)

    def run_hpon(self, args, bufsize=1048567, raise_on_error=True, ignore_error=False):
        cmd = self.hponcfg_path + ' ' + args
        return cli.run(cmd, bufsize=bufsize, raise_exception=raise_on_error,
                       ignore_error=ignore_error)

    def create_superuser(self, username, password, channels=(1, 2), user_id=2):
        raise NotImplemented

    def create_superuser_hp(self, username, password):
        self.run_hpon('-f %s -l %s' % (self.list_users_path, self.users_path))
        # noinspection PyUnresolvedReferences
        user_tree = etree.parse(self.users_path)
        user_elements = user_tree.xpath('.//USER_LOGIN')
        if user_elements:
            for user_element in user_elements:
                user = list(user_element.values())[0]
                self.run_hpon('-f %s -s user=%s' % (self.del_user_path, user))
        self.run_hpon('-f %s -s user=%s,password=%s' % (self.add_user_path, username, password))

    def bootstrap_obm_static(self, ip_address, netmask, gateway, username, password):
        self.configure_static_network(ip_address, netmask, gateway)
        self.create_superuser_hp(username, password)
        return self.verify_network_info(ip_address, netmask, gateway, 'static')

    def parse_network_info(self, channel=2):
        return super(IPMIToolHP, self).parse_network_info(channel=channel)
