import logging

import multiprocessing
import signal
import threading
import time

LOG = logging.getLogger('')


class Handler(logging.Handler):
    def emit(self, record):
        print(record.__dict__)


def func(i, s):
    cnt = 0
    while cnt < i:
        print('CYCLE: {}'.format(cnt))
        time.sleep(s)
        cnt += 1


def run_timeout(f, args=None, kwargs=None, timeout=10):
    # noinspection PyUnusedLocal
    def __handler(signum, frame):
        raise Exception('Function {} timed out bra!'.format(f.__name__))

    signal.signal(signal.SIGALRM, __handler)

    signal.alarm(timeout)
    args = args or []
    kwargs = kwargs or {}
    LOG.info('HELLO?')
    return f(*args, **kwargs)


def p_runner():
    try:
        run_timeout(func, [20, 1], timeout=5)
    except Exception as e:
        print('caught %s in process' % e)
        raise


def t_runner():
    p = multiprocessing.Process(target=p_runner, name='_xxx_yyyyy')
    try:
        p.start()
    except Exception as e:
        print('caught %s in thread' % e)
        raise

logging.basicConfig(level=logging.DEBUG)
h = Handler()
LOG.addHandler(h)

t = threading.Thread(target=t_runner)

t.start()
# t.join()
