import ast
import json

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
    """
    service_client = context.services[service_name]['client']
    data = context.services[service_name]['details']['query']

    # TODO: this is stupid, fix it
    # (going from string -> dict -> json)
    # TODO: also, in the feature file
    # you need to check that the query actually worked
    data = ast.literal_eval(ast.literal_eval(data))
    context.services[service_name]['resp'] = service_client.post(data=json.dumps(data),
        url_suffix="query")
