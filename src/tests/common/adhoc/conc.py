import logging
import multiprocessing
from mercury.common.transport import get_ctx_and_connect_req_socket,\
    full_req_transceiver

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

ZURL = 'tcp://localhost:9090'
# socka = get_ctx_and_connect_req_socket(ZURL)
# sockb = get_ctx_and_connect_req_socket(ZURL)


def transmit(action):
    r = full_req_transceiver(ZURL, action)
    log.info("Return: {}".format(r))


t1 = multiprocessing.Process(target=transmit, args=({'action': 'sleep'},))
t2 = multiprocessing.Process(target=transmit, args=({'action': 'fast'},))
t3 = multiprocessing.Process(target=transmit,
                             args=({'action': 'self-destruct'},))
t1.start()
t2.start()
t3.start()


input("Press enter")
