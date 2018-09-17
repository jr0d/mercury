import time
import json

import requests

from src.tests.behave.api.features.common.exception import TimeoutException


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
            "could not reach service: {1}".format(timeout, url)
        )
    return resp


def to_singular(name):
    """Convert the name to singular if it is plural

    This just trims a trailing 's', if found.
    """
    return name[:-1] if name.endswith("s") else name


def get_entity_list_container_field(name):
    """Returns the container field used in list responses

    GET /active_computers       -> {"items": [...]}
    GET /jobs                   -> {"jobs": [...]}
    """
    if name == "active_computers":
        return "items"
    elif name == "inventory_computers":
        return "items"
    elif name == "rpc_tasks":
        return "tasks"
    elif name == "rpc_jobs":
        return "jobs"
    return name


def get_entity_id_field(name):
    """Returns the id field used for entities in list responses

    GET /active_computers       -> {"items": [{"mercury_id": "...", ...}}]}
    GET /jobs                   -> {"jobs": [{"job_id": "...", ...}}]}
    """
    if name == "active_computers":
        return "mercury_id"
    elif name == "inventory_computers":
        return "mercury_id"
    elif name == "rpc_tasks":
        return "task_id"
    elif name == "rpc_jobs":
        return "job_id"
    return name


def read_json_from_file(filename, location):
    filename = "{0}/{1}".format(location, filename)
    with open(filename) as file:
        data = json.loads(file.read())
    return data


def wait_for_not_none(func, *args, timeout=20):
    value = func(*args)
    while value == None:
        if timeout <= 0:
            break
        time.sleep(5)
        timeout -= 1
        value = func(*args)
    return value


def keys_in_list_or_dict(key_stack, item):
    if len(key_stack) <= 0:
        return True
    else:
        key = key_stack[0]
        if type(item) == dict:
            if key not in item.keys():
                return False
            new_item = item[key]
            r = keys_in_list_or_dict(key_stack[1:], new_item)
            return r
        elif type(item) == list:
            results = True
            for sub in item:
                r = keys_in_list_or_dict(key_stack, sub)
                results = results and r
            return results
        else:
            return False


def check_params_applied_in_resp(param_data, resp):

    # TODO define checks for specific keys
    # for example the order and limit come back in the respnose

    all_matched = True

    keys = param_data.keys()
    for key in keys:
        # in case a key returned is a different string
        akey = key
        if param_data[key] == None:
            break
        if key == "limit":
            expected_result = param_data[key]
            if type(expected_result) is not int or expected_result < 0:
                expected_result = 250
            actual_result = resp.json()[akey]
            if expected_result != actual_result:
                all_matched = False
        elif key == "sort_direction":
            expected_result = param_data[key]
            if expected_result == -1:
                expected_result = "DESCENDING"
            else:
                expected_result = "ASCENDING"
            actual_result = resp.json()[akey]
            if expected_result != actual_result:
                all_matched = False
        elif key == "projection":
            projections = param_data[key].split(",")
            if "items" in resp.json().keys():
                if resp.json()["items"] == []:
                    return False
                    # TODO add a computer to the DB somehow
                else:
                    for item in resp.json()["items"]:
                        for projection in projections:
                            pstack = projection.split(".")
                            result = keys_in_list_or_dict(pstack, item)
                            all_matched = all_matched and result
            else:
                item = resp.json()
                for projection in projections:
                    pstack = projection.split(".")
                    result = keys_in_list_or_dict(pstack, item)
                    all_matched = all_matched and result

    return all_matched
