import json
import time
import operator
from functools import reduce

from behave import given, when, step
from src.tests.behave.api.features.common.utils import (
    get_entity_list_container_field,
    get_entity_id_field,
    read_json_from_file,
    wait_for_not_none,
)


@given(
    "I have job injection details in {filename} for creating jobs using the {service_name} api"
)
def step_i_have_job_injection_details_in_filename_for_creating_jobs_using_the_service_api(
    context, filename, service_name
):
    """
    :type context: behave.runner.Context
    :type service_name: str
    """
    location = context.json_location
    data = read_json_from_file(filename, location)

    context.services[service_name]["details"]["job_data"] = data


@given(
    "I have job injection details for a specific {device_service} device in {filename} for creating jobs using the {service_name} api"
)
def step_i_have_job_injection_details_for_specific_device_in_filename_for_creating_jobs_using_the_service_api(
    context, filename, service_name, device_service
):
    """
    :type context: behave.runner.Context
    :type service_name: str
    """
    location = context.json_location
    data = read_json_from_file(filename, location)
    data["query"]["mercury_id"] = context.services[device_service]["id"]

    context.services[service_name]["details"]["job_data"] = data


@when("I get the injection results from a post to {service_name}")
def step_i_get_the_injection_results_from_a_post_to_service_api(
    context, service_name
):
    """
    :type context: behave.runner.Context
    :type service_name: str
    """
    service_client = context.services[service_name]["client"]
    data = context.services[service_name]["details"]["job_data"]

    context.services[service_name]["resp"] = service_client.post(
        data=json.dumps(data)
    )


@when(
    "I get with bad headers in {filename} the injection results from a post to {service_name}"
)
def step_i_get_with_bad_headers_the_results_from_a_post_to_service(
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
    data = context.services[service_name]["details"]["job_data"]

    context.services[service_name]["resp"] = service_client.post(
        data=json.dumps(data), headers=headers
    )


@step("the response contains a {service_name} job_id")
def step_the_response_contains_a_job_id(context, service_name):
    """
    :type context: behave.runner.Context
    :type service_name: str
    """
    service_resp = context.services[service_name]["resp"]
    job_id = service_resp.json()["job_id"]
    context.check.assertIsInstance(job_id, str)
    context.services[service_name]["id"] = job_id
    # TODO is the job id valid?


@step(
    "the corresponding {service_name} job is completed with successful {tasks_service_name} tasks"
)
def step_the_corresponding_service_job_is_completed_and_successful(
    context, service_name, tasks_service_name
):
    """
    :type context: behave.runner.Context
    """
    service_client = context.services[service_name]["client"]
    service_resp = service_client.get(context.services[service_name]["id"])
    context.services[service_name]["resp"] = service_resp

    def get_time_completed(job_id):
        return service_client.get(job_id).json()["ttl_time_completed"]

    completed = wait_for_not_none(
        get_time_completed, context.services[service_name]["id"]
    )

    status_resp = service_client.get(
        context.services[service_name]["id"], url_suffix="status"
    )
    tasks = status_resp.json()["tasks"]
    context.services[tasks_service_name]["tasks"] = tasks
    statuses = [task["status"] for task in tasks]
    for status in statuses:
        context.check.assertEqual(status, "SUCCESS")
    has_failures = status_resp.json()["has_failures"]
    context.check.assertEqual(has_failures, False)

    # TODO is the job valid/working?


# Used for bad method testing
@when("I inject with {method} for {service_name}")
def step_i_use_method_on_inject_service(context, method, service_name):
    """
    :type context: behave.runner.Context
    :type method: str
    :type service_name: str
    """
    service_client = context.services[service_name]["client"]
    data = context.services[service_name]["details"]["job_data"]

    if method == "delete":
        context.services[service_name]["resp"] = service_client.delete()
    # TODO etc
