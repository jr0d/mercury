"""
Document schema:

    mercury_id:
    rpc_address:
    rpc_port:
    ping_address:
    ping_port:
    capabilities: [
        name:
        desc:
        args: int
        kwargs: [key1, key2, keyN]
        usage:
    ]
"""
import logging
import time

log = logging.getLogger(__name__)


class ActiveInventoryDBController(object):
    keys = ['mercury_id',
            'rpc_address',
            'rpc_address6',
            'rpc_port',
            'ping_port',
            'capabilities']

    def __init__(self, collection):
        self.collection = collection
        self.collection.ensure_index('mercury_id', unique=True)

    def validate(self, data):
        for k in self.keys:
            if k not in data:
                return False
        return True

    @staticmethod
    def data_format(data):
        return 'mercury_id: {mercury_id}, server: {rpc_address}, rpc_port: {rpc_port}, ' \
               'ping_port: {ping_port}'.format(**data)

    def insert(self, data):
        document = self.collection.find_one({'mercury_id': data['mercury_id']})

        data['time_created'] = time.time()

        if document:
            log.warning(
                'Attempted insert of existing object. Offending: %s' % data['mercury_id'])

            log.info('Performing update: %s' % self.data_format(data))
            self.collection.update_one({'mercury_id': data['mercury_id']}, {'$set': data})
            return document['_id']

        log.info(
            'Adding active inventory: %s' % self.data_format(data))
        return self.collection.insert_one(data).inserted_id

    def remove(self, mercury_id):
        log.debug('Removing mercury_id: %s' % mercury_id)
        document = self.collection.find_one_and_delete({'mercury_id': mercury_id},
                                                       projection=['mercury_id',
                                                                   'time_created'])
        if not document:
            log.info('%s was already removed' % mercury_id)
            return

        now = time.time()
        log.info('Removed mercury_id: %s, lived: %s' % (mercury_id,
                                                        now - document['time_created']))

    def get(self, mercury_id):
        return self.collection.find_one({'mercury_id': mercury_id})


if __name__ == '__main__':
    from mercury.common.mongo import get_collection
    logging.basicConfig(level=logging.DEBUG)

    _data = dict(mercury_id=1234, rpc_address='127.0.0.1', rpc_port=9002, ping_address='127.0.0.1', ping_port=9003,
                 capabilities={'echo': dict(desc='echo\'s argument[0] to the console', args=1, kwargs=[])})
    _collection = get_collection('test', 'mercury_rpc')
    aidbc = ActiveInventoryDBController(_collection)
    print aidbc.insert(_data)
    print aidbc.get(1234)
    aidbc.remove(1234)
