import json
import operator
from functools import reduce

from behave import given, when, step
from tests.api.features.common.utils import get_entity_list_container_field, get_entity_id_field, read_json_from_file


@given("I have job injection details in {filename} for creating jobs using the {service_name} api")
def step_i_have_job_injection_details_in_filename_for_creating_jobs_using_the_service_api(
        context, filename, service_name):
    """
    :type context: behave.runner.Context
    :type service_name: str
    """
    location = context.json_location
    data = read_json_from_file(filename, location)

    context.services[service_name]['details']['job_data'] = data

@when("I get the injection results from a post to {service_name}")
def step_i_get_the_injection_results_from_a_post_to_service_api(
        context, service_name):
    """
    :type context: behave.runner.Context
    :type service_name: str
    """
    service_client = context.services[service_name]['client']
    data = context.services[service_name]['details']['job_data']

    #context.services[service_name]['resp'] = \
    #    service_client.post(data=json.dumps(data))
    # TODO
    print("Posting data...")
    context.services[service_name]['resp'] = "Mock Resp"

@step("the response contains a {service_name} job_id")
def step_the_response_contains_a_job_id(
        context, service_name):
    """
    :type context: behave.runner.Context
    :type service_name: str
    """
    print("Checking for job id in response...")
    service_resp = context.services[service_name]['resp']
    print(service_resp)
    # TODO check that service resp contains a job_id

@step("the corresponding job is valid")
def step_the_corresponding_job_is_valid(
        context):
    """
    :type context: behave.runner.Context
    """
    print("Checking for valid job...")
    # TODO get job, check that job is valid
    context.check.assertIsNotNone(None)
