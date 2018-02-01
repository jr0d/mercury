import logging
import motor.motor_asyncio


log = logging.getLogger(__name__)


def get_connection(server_or_servers=None,
                   replica_set=None,
                   username=None,
                   password=None):
    servers = server_or_servers
    if servers is not None:
        if not isinstance(servers, list):
            servers = [servers]
    log.info('Connecting to %s : replicaSet: %s' % (servers, replica_set))

    if username:
        return motor.motor_asyncio.AsyncIOMotorClient(servers,
                                                      replicaset=replica_set,
                                                      username=username,
                                                      password=password)
    else:
        return motor.motor_asyncio.AsyncIOMotorClient(servers,
                                                      replicaset=replica_set)

