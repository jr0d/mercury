import random

from behave import when, step, then, given
from src.tests.behave.api.features.common.utils import (
    get_entity_list_container_field,
    read_json_from_file,
)


@when("I get the list of {service_name}")
def step_i_get_the_list_of_service(context, service_name):
    """
    :type context: behave.runner.Context
    :type service_name: str
    """
    service_client = context.services[service_name]["client"]
    context.services[service_name]["resp"] = service_client.get()


@when("I get with bad headers in {filename} the list of {service_name}")
def step_i_get_with_bad_headers_the_list_of_service(
    context, filename, service_name
):
    """
    :type context: behave.runner.Context
    :type service_name: str
    :type filename: str
    """

    location = context.json_location
    headers = read_json_from_file(filename, location)

    service_client = context.services[service_name]["client"]
    context.services[service_name]["resp"] = service_client.get(headers=headers)


@when("I get with parameters in {filename} the list of {service_name}")
def step_i_get_the_list_of_service_with_params_in_filename(
    context, service_name, filename
):
    """
    :type context: behave.runner.Context
    :type service_name: str
    :type filename: str
    """
    location = context.json_location
    data = read_json_from_file(filename, location)

    keys = data.keys()
    suffix = "?"
    for key in keys:
        suffix = "{0}{1}={2}&".format(suffix, key, data[key])
    # trim trailing &
    suffix = suffix.rstrip("&")
    context.services[service_name]["param_data"] = data
    service_client = context.services[service_name]["client"]
    context.services[service_name]["resp"] = service_client.get(
        url_suffix=suffix
    )


@step("I get with offset parameters in {filename} the list of {service_name}")
def step_i_get_the_offset_list_of_service_with_params_in_filename(
    context, service_name, filename
):
    """
    :type context: behave.runner.Context
    :type service_name: str
    :type filename: str
    """
    # TODO make this work locally with less results
    service_resp = context.services[service_name]["resp"]
    container_field = get_entity_list_container_field(service_name)
    service_entities = service_resp.json()[container_field]
    # TODO configure or calculate the indices
    offset_id = service_entities[4]["_id"]
    first_id = service_entities[5]["_id"]
    context.services[service_name]["offset_id"] = offset_id
    context.services[service_name]["first_id"] = first_id

    location = context.json_location
    data = read_json_from_file(filename, location)

    keys = data.keys()
    suffix = "?"
    for key in keys:
        if key == "offset_id":
            data["offset_id"] = offset_id
        suffix = "{0}{1}={2}&".format(suffix, key, data[key])
    # trim trailing &
    suffix = suffix.rstrip("&")
    context.services[service_name]["offset_param_data"] = data
    service_client = context.services[service_name]["client"]
    context.services[service_name]["offset_resp"] = service_client.get(
        url_suffix=suffix
    )


@step("the response contains a list of {service_name}")
def step_the_response_contains_a_list_of_service_ids(context, service_name):
    """
    :type context: behave.runner.Context
    :type service_name: str
    """
    service_resp = context.services[service_name]["resp"]
    container_field = get_entity_list_container_field(service_name)
    service_entities = service_resp.json()[container_field]
    context.check.assertIsInstance(service_entities, list)
    # TODO make sure the actual entities in the list are what they should be
    # WIP: Validate for service IDs


@step(
    "the response contains an offset list of {service_name} that have been offset by the offset_id"
)
def step_the_response_contains_a_list_of_service_ids(context, service_name):
    """
    :type context: behave.runner.Context
    :type service_name: str
    """
    service_resp = context.services[service_name]["offset_resp"]
    container_field = get_entity_list_container_field(service_name)
    service_entities = service_resp.json()[container_field]
    context.check.assertIsInstance(service_entities, list)
    first_entity = service_entities[0]
    first_id = context.services[service_name]["first_id"]
    offset_id = context.services[service_name]["offset_id"]
    context.check.assertEqual(first_entity["_id"], first_id)
    for entity in service_entities:
        context.check.assertNotEqual(entity["_id"], offset_id)
    # TODO make sure the actual entities in the list are what they should be
    # WIP: Validate for service IDs


@then("the entity is {existence} in the {service_name} list")
def step_the_entity_is_exists_in_the_service_list(
    context, existence, service_name
):
    """
    :type context: behave.runner.Context
    :param existence: can either be 'found' or 'not found'
    :type existence: str
    :type service_name: str
    """
    device_id = context.services[service_name]["id"]
    entities = context.services[service_name]["resp"].json()[service_name]
    if existence == "not found":
        context.check.assertNotIn(device_id, [entity.id for entity in entities])
    elif existence == "found":
        context.check.assertIn(device_id, [entity.id for entity in entities])
    else:
        raise Exception(
            "{} is not a valid existence name!  "
            "Please use 'found' or 'not found'"
        )
