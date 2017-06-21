import logging
import threading

from mercury.common.exceptions import MercuryGeneralException
from mercury.common.helpers import cli

log = logging.getLogger(__name__)
LLDPLITE_DEFAULT_PATH = 'lldplite'


class LLDPInspector(object):
    __key__ = 'lldplite'

    def __init__(self, device_info, backend_client, lldplite_path=LLDPLITE_DEFAULT_PATH):
        self.device_info = device_info
        self.backend_client = backend_client
        self.lldplite_path = lldplite_path
        self.lldplite = cli.find_in_path(lldplite_path)
        if not self.lldplite:
            raise MercuryGeneralException('Could not find lldplite binary')

        self.pids = {}

    def _run(self, interface):
        switch_info = get_lldp_info(interface, self.lldplite)
        self.process(interface, switch_info)

    def inspect(self):
        for i in self.device_info.get('interfaces', []):
            if i.get('carrier'):
                log.info('Interface {} is active, sniffing for LLDP packets'.format(i['devname']))
                p = threading.Thread(target=self._run, args=(i['devname'],))
                self.pids[i['devname']] = {'process': p, 'result': None}
                p.start()

    def get_interface_index(self, interface):
        interfaces = self.device_info.get('interfaces')
        if interfaces:
            for _i in range(len(interfaces)):
                if interfaces[_i]['devname'] == interface:
                    return _i
        log.error('{} index is somehow missing from device info'.format(interface))
        return -1

    def process(self, interface, switch_info):
        index = self.get_interface_index(interface)

        if not switch_info or index == -1:
            self.pids[interface]['result'] = {'missing': True}
            return

        self.backend_client.update(
            self.device_info['mercury_id'],
            {'interfaces.{}.lldp'.format(self.get_interface_index(interface)): switch_info})
        self.pids[interface]['result'] = switch_info

    def cleanup(self):
        pass


def get_lldp_info(interface, lldplight_path):
    command = '{} {}'.format(lldplight_path, interface)
    result = cli.run(command, raise_exception=False, quiet=True, ignore_error=True)

    if result.returncode == 5:
        log.debug('Timed out waiting for LLDP broadcast on {}'.format(interface))
        return None

    elif result.returncode:
        log.error("Problem running lldplite: {}".format(result.stderr))
        return None

    switch_name = result.split()[0]
    port_number = int(result.split()[1].split('/')[-1])

    log.info('LLDP info: {} {}'.format(switch_name, port_number))

    return {'switch_name': switch_name, 'port_number': port_number}
