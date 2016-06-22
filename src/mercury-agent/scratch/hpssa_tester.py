import logging

from hpssa import HPSSA

logging.basicConfig(level=logging.DEBUG)
logging.getLogger('mercury.common').setLevel(level=logging.WARN)
_hpssa = HPSSA()
from pprint import pprint
pprint(_hpssa.adapters)
print(_hpssa.cache_ok(0))

print(_hpssa.get_drive(0, '1I:1:19'))
# res = _hpssa.create(0, '1I:1:19,1I:1:20', 1)

# print res
# print res.stderr
# print res.returncode

pprint(_hpssa.get_pd_info(0, '1I:1:19'))
pprint(_hpssa.get_pd_info(0, _hpssa.get_pd_by_index(0, 19)))

pprint(_hpssa.adapters[0].total_size)
