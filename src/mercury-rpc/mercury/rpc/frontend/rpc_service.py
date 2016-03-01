import logging

from bottle import route, run, request, HTTPResponse

from mercury.common.inventory_client.client import InventoryClient  # TODO: Clean up import
from mercury.common.mongo import get_collection
from mercury.common.exceptions import MercuryCritical
from mercury.rpc.configuration import rpc_configuration, db_configuration
from mercury.rpc.jobs import Job, get_jobs_collection


log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

active_collection = get_collection(db_configuration.get('rpc_mongo_db',
                                                        'test'),
                                   db_configuration.get('rpc_mongo_collection',
                                                        'rpc'),
                                   server_or_servers=db_configuration.get('rpc_mongo_servers',
                                                                          'localhost'),
                                   replica_set=db_configuration.get('rpc_replica_set'))

jobs_collection = get_jobs_collection()

inventory_configuration = rpc_configuration.get('inventory', {})
inventory_router_url = inventory_configuration.get('inventory_router')

if not inventory_router_url:
    raise MercuryCritical('Configuration is missing or invalid')

inventory_client = InventoryClient(inventory_router_url)


def http_error(message, code=500):
    return HTTPResponse({'error': True, 'message': message}, status=code)


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
    projection_keys = request.query.get('projection', '')
    if projection_keys:
        projection = {}
        for k in projection_keys.split(','):
            projection[k] = 1
    else:
        projection = None  # An empty dict means no projections, not show me everything...

    c = inventory_client.get_one(mercury_id, projection=projection)

    if not computer:
        return http_error('mercury_id %s does not exist in inventory' % mercury_id,
                          404)

    return {'computer': c}


@route('/api/active/computers', method='GET')
def active_computers():
    cursor = active_collection.find({})
    active = []
    for document in cursor:
        document['_id'] = str(document['_id'])
        active.append(document)

    return {'active': active}


def query_active_prototype1(query):
    # Get all inventory matching inventory mercury_ids and iterate over
    inventory_matches = inventory_client.query(query)

    active_matches = []
    cursor = active_collection.find({})

    for active_document in cursor:
        for inventory_document in inventory_matches['items']:

            if active_document.get('mercury_id') == inventory_document.get('mercury_id'):
                active_matches.append(active_document)
                break

    return active_matches


@route('/api/rpc/inject', method='POST')
def inject():
    try:
        if not request.json:
            return http_error('JSON request is missing', code=400)
    except ValueError:
        return http_error('JSON request is malformed', code=400)

    # Using instance here because we are checking for
    query = request.json.get('query')
    if not isinstance(query, dict):
        return http_error('Query is missing from request', code=400)

    command = request.json.get('command')
    if not isinstance(command, dict):
        return http_error('Command is missing from request or is malformed', code=400)

    active_matches = query_active_prototype1(query)
    log.debug('Matched %d active computers' % len(active_matches))
    job = Job(command, active_matches, jobs_collection)
    job.start()

    return {'job_id': str(job.job_id)}

run(host='localhost', port=9005, debug=True)
