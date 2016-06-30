import logging
import threading
import time

from mercury.common.exceptions import MercuryGeneralException
from mercury.common.helpers import cli

log = logging.getLogger(__name__)
LLDPLITE_DEFAULT_PATH = './lldplite.sh'


class LLDPInspector(object):
    def __init__(self, device_info, agent_configuration, lldplite_path=LLDPLITE_DEFAULT_PATH):
        self.device_info = device_info
        self.configuration = agent_configuration
        self.lldplite_path = lldplite_path
        self.lldplite = cli.find_in_path(lldplite_path)
        if not self.lldplite:
            raise MercuryGeneralException('Could not find lldplite binary')

        self.pids = {}

    def _run(self, interface):
        result = cli.run('{} {}'.format(self.lldplite, interface), ignore_error=True,
                         raise_exception=False, quiet=True)

        if result.returncode == 5:
            log.info('LLDP timeout on {}'.format(interface))
        self.process(interface, result)

    def inspect(self):
        for i in self.device_info.get('interfaces', []):
            if i.get('carrier'):
                log.info('Interface {} is active, sniffing for LLDP packets'.format(i['devname']))
                p = threading.Thread(target=self._run, args=(i,))
                self.pids[i] = {'process': p, 'result': None}
                p.start()

    def get_interface_index(self, interface):
        interfaces = self.device_info.get('interfaces')
        if interfaces:
            for _i in range(len(interfaces)):
                if interfaces[_i]['devname'] == interface:
                    return _i
        return -1

    def process(self, interface, switch_info):
        interface_index = self.get_interface_index(interface)
        if not interface_index:
            raise MercuryGeneralException('Interface is missing somehow')

        update_data = {
            'mercury_id': self.device_info['mercury_id'],
            'update_data':
                {
                    'interfaces.{interface_index}.lldp_info_lite': switch_info
                }
        }

    def cleanup(self):
        pass


def get_lldp_info(interface, lldplight_path=LLDPLITE_DEFAULT_PATH):
    _path = cli.find_in_path(lldplight_path)

    if not _path:
        log.error('lldplite does not exist in path')
        return None

    command = '{} {}'.format(_path, interface)
    result = cli.run(command)

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

# Find all interfaces

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    l = LLDPInspector(None, None, 'lldplite.sh')
    l.inspect()
    try:
        time.sleep(15)
    except KeyboardInterrupt:
        import sys
        sys.exit(0)
    finally:
        print(l.pids)

