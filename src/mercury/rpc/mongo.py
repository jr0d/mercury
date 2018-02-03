from mercury.common import mongo as common_mongo
from mercury.common.asyncio import mongo as asyncio_mongo

__rpc_collections = None


class RPCCollection(object):
    """ The purpose of this class is to provide the multiple RPC layer services
    a single place to configure and instantiate database connections. """

    def __init__(self, servers, database, jobs_collection, tasks_collection,
                 replica_name=None, username=None, password=None,
                 use_asyncio=False):
        """ Constructor

        :param servers: MongoDB servers to connect to connect to
        :type servers: list
        :param database: The database to use for both collections
        :param jobs_collection: The name of the jobs collection
        :param tasks_collection: The name of the tasks collection
        :param replica_name: The name of the replica set to use, if any
        :param username:
        :param password:
        :param use_asyncio: Use asyncio for the connection object or not
        """
        self.servers = servers
        self.database = database
        self.jobs_collection_name = jobs_collection
        self.tasks_collection_name = tasks_collection
        self.replica_name = replica_name
        self.username = username
        self.password = password
        self.use_asyncio = use_asyncio

        # Caches
        self.__connection = None
        self.__jobs = None
        self.__tasks = None

    @property
    def connection(self):
        if not self.__connection:
            if self.use_asyncio:
                self.__connection = asyncio_mongo.get_connection(
                    self.servers, self.replica_name, username=self.username,
                    password=self.password
                )
            else:
                self.__connection = common_mongo.get_connection(
                    self.servers, self.replica_name, username=self.username,
                    password=self.password)
        return self.__connection

    @property
    def jobs_collection(self):
        if not self.__jobs:
            self.__jobs = common_mongo.get_collection(
                self.database,
                self.jobs_collection_name,
                self.connection)
        return self.__jobs

    @property
    def tasks_collection(self):
        if not self.__tasks:
            self.__tasks = common_mongo.get_collection(
                self.database,
                self.tasks_collection_name,
                self.connection
            )
        return self.__tasks


def init_rpc_collections(servers, database, jobs_collection, tasks_collection,
                         replica_name=None, username=None, password=None, use_asyncio=False):
    global __rpc_collections
    if not __rpc_collections:
        __rpc_collections = RPCCollection(servers, database, jobs_collection,
                                          tasks_collection, replica_name, username,
                                          password,
                                          use_asyncio)
    return __rpc_collections


def get_rpc_collections():
    """ Accessor for factory instance"""
    if not __rpc_collections:
        raise RuntimeError('RPCCollectionFactory must be instantiated!')
    return __rpc_collections
