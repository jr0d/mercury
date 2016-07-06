import logging
import threading
import time

from mercury.common.exceptions import MercuryGeneralException
from mercury.common.helpers import cli

log = logging.getLogger(__name__)
LLDPLITE_DEFAULT_PATH = 'lldplite'


class LLDPInspector(object):
    __key__ = 'lldplite'

    def __init__(self, device_info, inventory_client, lldplite_path=LLDPLITE_DEFAULT_PATH):
        self.device_info = device_info
        self.inventory_client = inventory_client
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
        return -1

    def process(self, interface, switch_info):
        if switch_info:
            self.inventory_client.update_one(
                self.device_info['mercury_id'],
                {'$push': {self.__key__: dict(interface=interface, **switch_info)}})
            self.pids[interface]['result'] = switch_info
        else:
            self.pids[interface]['result'] = {'error': True}

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

# Find all interfaces

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    device_info = {
        'mercury_id': '1234',
        'interfaces': [
            {'devname': 'eth0', 'carrier': True},
            {'devname': 'eth1', 'carrier': True}
        ]
    }

    class IC(object):
        @staticmethod
        def update_one(m_id, data):
            print('M_ID => {}, {}'.format(m_id, data))

    logging.basicConfig(level=logging.DEBUG)
    l = LLDPInspector(device_info, IC(), '/home/jared/git/lldpr/lldplite')

    l.inspect()
    try:
        time.sleep(3)
    except KeyboardInterrupt:
        import sys
        sys.exit(0)
    finally:
        print(l.pids)

