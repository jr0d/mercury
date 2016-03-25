import logging

from bottle import route, run, request, HTTPResponse

from mercury.common.inventory_client.client import InventoryClient  # TODO: Clean up import
from mercury.common.mongo import get_collection
from mercury.common.exceptions import MercuryCritical, MercuryUserError
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


def check_json():
    try:
        if not request.json:
            return http_error('JSON request is missing', code=400)
    except ValueError:
        return http_error('JSON request is malformed', code=400)


def get_projection_from_qsa():
    projection_keys = request.query.get('projection', '')
    projection = {}
    if projection_keys:
        for k in projection_keys.split(','):
            projection[k] = 1

    return projection or None


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
    projection = get_projection_from_qsa()
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


def get_active():
    # Using instance here because we are checking for
    query = request.json.get('query')
    if not isinstance(query, dict):
        return http_error('Query is missing from request', code=400)

    return query_active_prototype1(query)


@route('/api/rpc/job/<job_id>', method='GET')
def get_job(job_id):
    projection = get_projection_from_qsa()
    job = jobs_collection.find_one({'job_id': job_id}, projection=projection)
    job['_id'] = str(job['_id'])
    return {'job': job}


@route('/api/rpc/jobs', method='GET')
def get_jobs():
    projection = get_projection_from_qsa()
    if not projection:
        projection = {'tasks': False}
    c = jobs_collection.find({}, projection=projection).sort('time_created', 1)
    count = c.count()
    jobs = []
    for job in c:
        job['_id'] = str(job['_id'])
        jobs.append(job)
    return {'count': count, 'jobs': list(jobs)}


@route('/api/rpc/jobs', method='POST')
def post_jobs():
    check_json()
    instruction = request.json.get('instruction')
    if not isinstance(instruction, dict):
        return http_error('Command is missing from request or is malformed', code=400)

    active_matches = get_active()
    log.debug('Matched %d active computers' % len(active_matches))
    # request.json.get('asset_backend')?
    # request.json.get('assets')?
    try:
        job = Job(instruction, active_matches, jobs_collection)
    except MercuryUserError as mue:
        return http_error(str(mue), code=400)
    job.start()

    return {'job_id': str(job.job_id)}


@route('/api/orca/press', method='POST')
def post_orca_press_job():
    check_json()
    query = request.json.get('query')
    if not isinstance(query, dict):
        return http_error('Query is missing from request', code=400)

run(host='localhost', port=9005, debug=True)
