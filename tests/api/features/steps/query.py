import ast
import json
import operator
from functools import reduce

from behave import given, when, step

@given("I have 'query' details for entities using the {service_name} api")
def step_i_have_create_details_for_the_entity_using_the_service_api(
        context, service_name):
    """
    :type context: behave.runner.Context
    :type service_name: str
    """
    context.services[service_name]['details']['query'] = json.dumps(context.text)

@when("I get the query_results from a query of {service_name}")
def step_i_get_the_query_results_from_a_query_of_service_api(
        context, service_name):
    """
    :type context: behave.runner.Context
    :type service_name: str
    """
    service_client = context.services[service_name]['client']
    data = context.services[service_name]['details']['query']

    # TODO: this is stupid, fix it
    # (going from string -> dict -> json)
    # TODO: also, in the feature file
    # you need to check that the query actually worked
    data = ast.literal_eval(ast.literal_eval(data))
    # TODO consider moving "query" to a config
    context.services[service_name]['resp'] = service_client.post(data=json.dumps(data),
        url_suffix="query")

@step("the {service_name} entities in the response contain {field} with {value}")
def step_the_entities_in_the_response_contain_field_with_value(
        context, service_name, field, value):
    """
    :type context: behave.runner.Context
    :type service_name: str
    :type field: str
    :type value: str
    """
    service_client = context.services[service_name]['client']
    service_resp = context.services[service_name]['resp']
    # TODO?
    # active computers are listed in the "items" field
    service_entities = service_resp.json()['items']
    context.check.assertGreater(len(service_entities),0)

    for entity in service_entities:
        # TODO this is ugly and mercury_id should be defined in a config
        entity_id = entity["mercury_id"]
        resp = service_client.get(entity_id)
        field = field.replace("'","")
        value = value.replace("'","")
        keys = field.split(".")
        actual_value = str(reduce(operator.getitem, keys, resp.json()))

        context.check.assertEqual(value, actual_value)
