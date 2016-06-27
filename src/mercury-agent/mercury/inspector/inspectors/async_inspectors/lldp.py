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
        try:
            self.pids[interface]['result'] = cli.run('{} {}'.format(self.lldplite, interface), ignore_error=True,
                                                     raise_exception=False, quiet=True)
        except Exception as e:
            print(e)

    def inspect(self):
        interfaces = [1, 2, 3, 4]
        for i in interfaces:
            p = threading.Thread(target=self._run, args=(i,))
            self.pids[i] = {'process': p, 'result': None}
            p.start()

    def process(self, result):
        # Update DB
        pass

    def cleanup(self):
        pass


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    l = LLDPInspector(None, None,
                      '/Users/jared/git/mercury/src/mercury-agent/mercury/inspector/'
                      'inspectors/async_inspectors/lldplite.sh')
    l.inspect()
    try:
        time.sleep(15)
    except KeyboardInterrupt:
        import sys
        sys.exit(0)
    finally:
        print(l.pids)

