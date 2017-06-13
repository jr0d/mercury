import logging
import motor.motor_asyncio


log = logging.getLogger(__name__)


def get_connection(server_or_servers=None, replica_set=None):
    servers = server_or_servers
    if servers is not None:
        if not isinstance(servers, list):
            servers = [servers]
    log.info('Connecting to %s : replicaSet: %s' % (servers, replica_set))
    return motor.motor_asyncio.AsyncIOMotorClient(servers, replicaset=replica_set)

