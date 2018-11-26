import json
import operator
from functools import reduce

from behave import given, when, step
from src.tests.behave.api.features.common.utils import (
    get_entity_list_container_field,
    get_entity_id_field,
    read_json_from_file,
)


@given(
    "I have query details in {filename} for entities using the {service_name} api"
)
def step_i_have_query_details_in_filename_for_entities_using_the_service_api(
    context, filename, service_name
):
    """
    :type context: behave.runner.Context
    :type filename: str
    :type service_name: str
    """
    location = context.json_location
    data = read_json_from_file(filename, location)

    context.services[service_name]["details"]["query"] = data


@when("I get the query_results from a query of {service_name}")
def step_i_get_the_query_results_from_a_query_of_service_api(
    context, service_name
):
    """
    :type context: behave.runner.Context
    :type service_name: str
    """
    service_client = context.services[service_name]["client"]
    data = context.services[service_name]["details"]["query"]

    context.services[service_name]["resp"] = service_client.post(
        data=json.dumps(data), url_suffix="query"
    )


@when(
    "I get with bad headers in {filename} the query_results from a query of {service_name}"
)
def step_i_get_the_query_results_from_a_query_of_service_api(
    context, filename, service_name
):
    """
    :type context: behave.runner.Context
    :type service_name: str
    :type filename: str
    """
    service_client = context.services[service_name]["client"]
    data = context.services[service_name]["details"]["query"]

    location = context.json_location
    headers = read_json_from_file(filename, location)

    context.services[service_name]["resp"] = service_client.post(
        data=json.dumps(data), url_suffix="query", headers=headers
    )


@when(
    "I get with parameters in {filename} the query_results from a query of {service_name}"
)
def step_i_get_the_query_results_from_a_query_with_params_in_filename_of_service_api(
    context, filename, service_name
):
    """
    :type context: behave.runner.Context
    :type filename: str
    :type service_name: str
    """

    location = context.json_location
    param_data = read_json_from_file(filename, location)

    keys = param_data.keys()
    suffix = "query?"
    for key in keys:
        suffix = "{0}{1}={2}&".format(suffix, key, param_data[key])
    # trim trailing &
    suffix = suffix.rstrip("&")
    context.services[service_name]["param_data"] = param_data

    service_client = context.services[service_name]["client"]
    data = context.services[service_name]["details"]["query"]

    context.services[service_name]["resp"] = service_client.post(
        data=json.dumps(data), url_suffix=suffix
    )


@step(
    "I get with offset parameters in {filename} the query_results from a query of {service_name}"
)
def step_i_get_the_offset_query_results_from_a_query_with_params_in_filename_of_service_api(
    context, filename, service_name
):
    """
    :type context: behave.runner.Context
    :type filename: str
    :type service_name: str
    """

    service_resp = context.services[service_name]["resp"]
    container_field = get_entity_list_container_field(service_name)
    service_entities = service_resp.json()[container_field]
    # TODO configure or calculate the indices
    offset_id = service_entities[4]["_id"]
    first_id = service_entities[5]["_id"]
    context.services[service_name]["offset_id"] = offset_id
    context.services[service_name]["first_id"] = first_id

    location = context.json_location
    param_data = read_json_from_file(filename, location)

    keys = param_data.keys()
    suffix = "query?"
    for key in keys:
        if key == "offset_id":
            param_data["offset_id"] = offset_id
        suffix = "{0}{1}={2}&".format(suffix, key, param_data[key])
    # trim trailing &
    suffix = suffix.rstrip("&")
    context.services[service_name]["offset_param_data"] = param_data

    service_client = context.services[service_name]["client"]
    data = context.services[service_name]["details"]["query"]

    context.services[service_name]["offset_resp"] = service_client.post(
        data=json.dumps(data), url_suffix=suffix
    )
    # so we can use existing checks on this response too
    context.services[service_name]["resp"] = context.services[service_name][
        "offset_resp"
    ]


@step(
    "the {service_name} entities in the response contain the data from {filename}"
)
def step_the_entities_in_the_response_contain_the_data_from_filename(
    context, service_name, filename
):
    """
    :type context: behave.runner.Context
    :type service_name: str
    :type field: str
    :type value: str
    """
    service_client = context.services[service_name]["client"]
    service_resp = context.services[service_name]["resp"]
    container_field = get_entity_list_container_field(service_name)
    service_entities = service_resp.json()[container_field]
    # TODO if len is 0 add a computer somehow
    context.check.assertGreater(len(service_entities), 0)

    field_name = get_entity_id_field(service_name)
    query_data = context.services[service_name]["details"]["query"]
    for entity in service_entities:
        # Make a call for each returned entity
        entity_id = entity[field_name]
        resp = service_client.get(entity_id)

        query = query_data["query"]
        for key in query.keys():
            # find the expected value for each key in the query
            value = query[key]
            # find the actual value from the http response
            keys = key.split(".")
            try:
                actual_value = reduce(operator.getitem, keys, resp.json())
                context.check.assertEqual(value, actual_value)
            except TypeError:
                # The computer doesn't have an "active" dictionary to check
                # the values of, it likely went inactive after the initial query
                pass


# Used for bad method testing
@when("I query with {method} for {service_name}")
def step_i_use_method_on_query_service(context, method, service_name):
    """
    :type context: behave.runner.Context
    :type method: str
    :type service_name: str
    """
    service_client = context.services[service_name]["client"]
    data = context.services[service_name]["details"]["query"]

    if method == "get":
        context.services[service_name]["resp"] = service_client.get(
            url_suffix="query"
        )
    elif method == "post":
        context.services[service_name]["resp"] = service_client.post(
            data=json.dumps(data), url_suffix="query"
        )
    # TODO etc
