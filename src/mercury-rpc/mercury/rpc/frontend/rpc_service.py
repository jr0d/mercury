import logging

from bottle import abort, route, run, request, response, HTTPResponse

from mercury.common.inventory_client.client import InventoryClient  # TODO: Clean up import
from mercury.common.mongo import get_collection
from mercury.rpc.configuration import rpc_configuration
from mercury.rpc.db import ActiveInventoryDBController

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

db_configuration = rpc_configuration.get('db', {})
active_collection = get_collection(db_configuration.get('rpc_mongo_db',
                                                        'test'),
                                   db_configuration.get('rpc_mongo_collection',
                                                        'rpc'),
                                   server_or_servers=db_configuration.get('rpc_mongo_servers',
                                                                          'localhost'),
                                   replica_set=db_configuration.get('replica_set'))

inventory_configuration = rpc_configuration.get('inventory', {})
inventory_router_url = inventory_configuration.get('inventory_router')

inventory_client = InventoryClient(inventory_router_url)


def http_error(message, code=500):
    return HTTPResponse({'error': True, 'message': message}, status=code)

@route('/api/active/', method='GET')
def active():
    adbc = ActiveInventoryDBController(active_collection)
    res = list(adbc.query({}))

    for i in res:
        if '_id' in i:
            i['_id'] = str(i['_id'])
    return {'active': res}
    # return {'hello': 'world'}


@route('/api/inventory/computers', method='GET')
def computers():
    return {'computers': inventory_client.query({})}


@route('/api/inventory/computers/query', method='POST')
def computers_query():
    if not request.json:
        return http_error('JSON request is missing', code=400)

    query = request.json.get('query')
    if not isinstance(query, dict):
        return http_error('Query is missing from request', code=400)
    return {'computers': inventory_client.query(query)}


@route('/api/inventory/computer/<mercury_id>', method='GET')
def computer(mercury_id):
    print request.body.read()
    if request.json:
        projection = request.json.get('projection')
    else:
        projection = None

    computer = inventory_client.get_one(mercury_id, projection=projection)

    if not computer:
        return http_error('mercury_id %s does not exist in inventory' % mercury_id,
                          404)

    return {'computer': computer}

run(host='localhost', port=9005, debug=True)
