# Copyright 2015 Jared Rodriguez (jared.rodriguez@rackspace.com)
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import logging
import msgpack
import threading
import time
import zmq

log = logging.getLogger(__name__)

RETRIES = 3  # TODO: YAML
PING_TIMEOUT = 2000  # TODO: YAML
BACK_OFF = .2


def ping(ctx, zurl, timeout=2500):
    _payload = {
        'message': 'ping',
        'timestamp': time.time()
    }
    socket = ctx.socket(zmq.REQ)
    socket.connect(zurl)

    log.debug('Pinging %s , payload: %s, timeout: %d' % (zurl, _payload, timeout))
    socket.send(msgpack.packb(_payload))

    if not socket.poll(timeout):
        log.debug('Ping timeout: %s' % zurl)
        socket.close()
        return False

    reply = socket.recv()
    log.debug("%s : %s" % (zurl, msgpack.unpackb(reply, encoding='utf-8')))
    socket.close()
    return True


if __name__ == '__main__':
    from mercury.rpc.db import ActiveInventoryDBController
    from mercury.rpc.configuration import rpc_configuration
    from mercury.common.mongo import get_collection

    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s : %(levelname)s - %(name)s - %(message)s')
    logging.getLogger('mercury.rpc.ping').setLevel(logging.DEBUG)
    db_configuration = rpc_configuration.get('db', {})
    collection = get_collection(db_configuration.get('rpc_mongo_db',
                                                     'test'),
                                db_configuration.get('rpc_mongo_collection',
                                                     'rpc'),
                                server_or_servers=db_configuration.get('rpc_mongo_servers',
                                                                       'localhost'),
                                replica_set=db_configuration.get('replica_set'))
    _db_controller = ActiveInventoryDBController(collection=collection)
