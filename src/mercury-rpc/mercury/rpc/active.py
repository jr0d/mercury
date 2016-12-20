"""
This is just too complex.. it's hard to get behind. Using something out of the box.. or
 sticking with the one thread per active inventory may have to do for now.


"""

import logging
import threading
import time

from mercury.common.task_managers.base.manager import Manager
from mercury.common.task_managers.base.task import Task
from mercury.rpc.ping2 import ping

# install future package for py2 compatibility
# noinspection PyCompatibility
from queue import Queue

__all__ = ['ActiveInventoryRuntimeHandler']

log = logging.getLogger(__name__)


global_lock = threading.Lock()

runtime_inventory = []
ping_queue = Queue()  # Quick workers
backoff_queue = Queue()  # Slow workers


class PingTask(Task):
    def __init__(self, ctx, timeout):
        super(PingTask, self).__init__()
        self.ctx = ctx
        self.timeout = timeout

    def fetch(self):
        return ping_queue.get()

    def do(self):
        mercury_id = self.task.get('mercury_id')
        address = self.task.get('rpc_address6') or self.task.get('rpc_address')
        port = self.task.get('ping_port')

        url = 'tcp://{address}:{port}'.format(address=address, port=port)

        log.debug('pinging {} : {}'.format(url, mercury_id))

        if not ping(self.ctx, url, timeout=self.timeout):
            log.debug('Initial ping failed, adding to backoff queue')
            backoff_queue.put(self.task)
        else:
            self.task.update({'working': False, 'ping_time': time.time()})

    @classmethod
    def create(cls):
        return cls(None)


class ActiveInventoryRuntimeHandler(object):
    """
    Maintains a list of active inventory devices for the purpose of pinging them.
    This approach was taken to avoid unnecessary database access.
    """

    def __init__(self, db_controller):
        """

        :param db_controller:
        """

        self.db_controller = db_controller

        self.lock = threading.Lock()

    @staticmethod
    def __validate_small(record):
        """
        Validate the bare necessities
        :param record:
        :return bool:
        """
        mercury_id = ('mercury_id', record.get('mercury_id'))
        address = ('address', record.get('rpc_address6') or record.get('rpc_address'))
        port = ('port', record.get('ping_port'))

        valid = True

        for name, _v in [mercury_id, address, port]:
            if not _v:
                log.error('Database entry for {} is missing {}'.format(
                    mercury_id or 'UNKONNW', name))
                valid = False

        return valid

    def reacquire(self):
        cursor = self.db_controller.query({}, projection={'mercury_id': 1,
                                                          'rpc_address': 1,
                                                          'rpc_address6': 1,
                                                          'ping_port': 1})

        log.debug('Reacquiring {} devices'.format(cursor.count()))

        for record in cursor:
            if not self.__validate_small(record):
                log.warning('Encountered junk in database: {}'.format(record['_id']))
                self.db_controller.collection.delete_one({'_id': record['_id']})
                continue
            log.debug('Reacquiring {}'.format(record['mercury_id']))
            self.append(record)

    @staticmethod
    def append(data):
        minimal_record = {
            'mercury_id': data['mercury_id'],
            'rpc_address': data['rpc_address'],
            'rpc_address6': data['rpc_address6'],
            'ping_port': data['ping_port'],
            'ping_time': 0,
            'ping_retries': 0,
            'working': False
        }
        runtime_inventory.append(minimal_record)

    @staticmethod
    def get(mercury_id):
        for record in runtime_inventory:
            if record['mercury_id'] == mercury_id:
                return record

    def exists(self, mercury_id):
        return bool(self.get(mercury_id))

    def register(self, record):
        if not self.db_controller.validate(record):
            return False

        if not self.db_controller.exists(record['mercury_id']):
            log.info('Adding active device: {}'.format(record['mercury_id']))
            self.db_controller.insert(record, perform_update=False)
        else:
            log.warning('Attempting to register existing device {}'.format(record['mercury_id']))

        if not self.exists(record['mercury_id']):
            self.append(record)

    def shutdown(self):
        pass
