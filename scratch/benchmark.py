import threading

from mercury.common.clients.rpc.backend import BackEndClient


zurl = 'tcp://0.0.0.0:9002'


def worker(number_of_transmissions):
    be = BackEndClient(zurl)
    worker_existing_socket(be, number_of_transmissions)


def worker_existing_socket(be, number_of_transmissions):
    for _ in range(number_of_transmissions):
        # noinspection PyBroadException
        try:
            be.transceiver(dict(incorrect='payload'))
        except:
            pass


def make_threads(workers, number_of_transmissions):
    tasks = []
    for _ in range(workers):
        tasks.append(threading.Thread(target=worker, args=(number_of_transmissions,)))
    return tasks


def start_threads(threads):
    for thread in threads:
        thread.start()


if __name__ == '__main__':
    ts = make_threads(2, 2000)
    start_threads(ts)
