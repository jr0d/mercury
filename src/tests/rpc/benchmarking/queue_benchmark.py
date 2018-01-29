import logging
import time

from multiprocessing.pool import Pool

from mercury.common.clients.router_req_client import RouterReqClient

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

TEST_NO_ASYNC_URL = 'tcp://localhost:9001'
TEST_ASYNC_URL = 'tcp://localhost:9002'

payload = {
    'endpoint': 'enqueue_task',
    'args':
        [{
            'host': 'localhost',
            'port': 9090,
            'method': 'echo',
            'args': ['Hello World!'],
            'kwargs': {},
            'task_id': '1',
            'job_id': '1',
        }]
}


def timer(func):
    def function_timer(*args, **kwargs):
        start = time.time()
        value = func(*args, **kwargs)
        end = time.time()
        runtime = end - start
        log.info(f"{func} took {runtime} seconds to complete")
        return value
    return function_timer


def work(url, n):
    client = RouterReqClient(url)

    results = [client.transceiver(payload) for _ in range(n)]
    client.close()
    return results


@timer
def concurrent_test(c, reqs, use_async):
    pool = Pool(processes=c)

    url = use_async and TEST_ASYNC_URL or TEST_NO_ASYNC_URL

    n = round(reqs / c)

    log.info(f'Starting test [Concurrency: {c}  Requests: {reqs} Async: '
             f'{use_async} ]')
    results = [pool.apply_async(work, (url, n)) for _ in range(c)]

    # wait
    [result.get() for result in results]

    pool.terminate()
    pool.close()


if __name__ == '__main__':
    concurrent_test(10, 1000, use_async=False)
    concurrent_test(10, 1000, use_async=True)

    concurrent_test(15, 2000, use_async=False)
    concurrent_test(15, 2000, use_async=True)
