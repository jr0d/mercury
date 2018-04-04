import time
import json

import requests

from tests.api.features.common.exception import TimeoutException


def check_service_api(url, interval_time=5, timeout=20):
    """Check for running service API

    :type url: str
    :type interval_time: int
    :type timeout: int

    """
    end_time = time.time() + timeout

    while time.time() < end_time:
        try:
            resp = requests.get(url)
        except requests.exceptions.RequestException:
            time.sleep(interval_time)
            continue
        if resp.status_code:
            break
    else:
        raise TimeoutException(
            "check_service_api ran for {0} seconds and "
            "could not reach service: {1}".format(timeout, url))
    return resp


def to_singular(name):
    """Convert the name to singular if it is plural

    This just trims a trailing 's', if found.
    """
    return name[:-1] if name.endswith('s') else name


def get_entity_list_container_field(name):
    """Returns the container field used in list responses

    GET /active_computers       -> {"items": [...]}
    GET /jobs                   -> {"jobs": [...]}
    """
    if name == 'active_computers':
        return 'items'
    elif name == 'inventory_computers':
        return 'items'
    elif name == 'rpc_tasks':
        return 'tasks'
    elif name == 'rpc_jobs':
        return 'jobs'
    return name

def get_entity_id_field(name):
    """Returns the id field used for entities in list responses

    GET /active_computers       -> {"items": [{"mercury_id": "...", ...}}]}
    GET /jobs                   -> {"jobs": [{"job_id": "...", ...}}]}
    """
    if name == 'active_computers':
        return 'mercury_id'
    elif name == 'inventory_computers':
        return 'mercury_id'
    elif name == 'rpc_tasks':
        return 'task_id'
    elif name == 'rpc_jobs':
        return 'job_id'
    return name

def read_json_from_file(filename, location):
    filename = "{0}/{1}".format(location, filename)
    with open(filename) as file:
        data = json.loads(file.read())

    return data
