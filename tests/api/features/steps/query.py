import json
import operator
from functools import reduce

from behave import given, when, step
from tests.api.features.common.utils import get_entity_list_container_field, get_entity_id_field


@given("I have 'query' details in {filename} for entities using the {service_name} api")
def step_i_have_query_details_in_filename_for_entities_using_the_service_api(
        context, filename, service_name):
    """
    :type context: behave.runner.Context
    :type service_name: str
    """

    # TODO pull this code out into a function in a common module
    filename = "{0}/{1}".format(context.json_location, filename)
    with open(filename) as file:
        data = json.loads(file.read())

    context.services[service_name]['details']['query'] = data

@when("I get the query_results from a query of {service_name}")
def step_i_get_the_query_results_from_a_query_of_service_api(
        context, service_name):
    """
    :type context: behave.runner.Context
    :type service_name: str
    """
    service_client = context.services[service_name]['client']
    data = context.services[service_name]['details']['query']

    context.services[service_name]['resp'] = \
        service_client.post(data=json.dumps(data), url_suffix="query")

@step("the {service_name} entities in the response contain the data from {filename}")
def step_the_entities_in_the_response_contain_the_data_from_filename(
        context, service_name, filename):
    """
    :type context: behave.runner.Context
    :type service_name: str
    :type field: str
    :type value: str
    """
    service_client = context.services[service_name]['client']
    service_resp = context.services[service_name]['resp']
    container_field = get_entity_list_container_field(service_name)
    service_entities = service_resp.json()[container_field]
    context.check.assertGreater(len(service_entities),0)

    field_name = get_entity_id_field(service_name)
    query_data = context.services[service_name]['details']['query']
    for entity in service_entities:
        # Make a call for each returned entity
        entity_id = entity[field_name]
        resp = service_client.get(entity_id)

        query = query_data['query']
        for key in query.keys():
            # find the expected value for each key in the query
            value = query[key]
            # find the actual value from the http response
            keys = key.split(".")
            actual_value = reduce(operator.getitem, keys, resp.json())
            context.check.assertEqual(value, actual_value)
