from behave import when, step
from src.tests.behave.api.features.common.utils import (
    get_entity_list_container_field,
    get_entity_id_field,
    read_json_from_file,
)


@step("a {service_name} entity id is located for testing")
def step_a_service_id_is_located_for_testing(context, service_name):
    """
    :type context: behave.runner.Context
    :type service_name: str
    """
    # Find a valid service entity from list call
    context.services[service_name]["id"] = None
    service_client = context.services[service_name]["client"]
    response = service_client.get()

    container_field = get_entity_list_container_field(service_name)
    field_name = get_entity_id_field(service_name)
    try:
        # TODO config value?
        service_entities = response.json()[container_field]
        # TODO if this is empty add one somehow?
        context.check.assertGreater(len(service_entities), 0)
        entity_id = service_entities[0][field_name]
        context.services[service_name]["id"] = entity_id
    except IndexError:
        context.check.assertIsNotNone(
            context.services[service_name]["id"],
            msg="WIP: Create {} API Not Yet Implemented".format(service_name),
        )
        # TODO: Create new service entity since we don't have any


@step("a {service_name} entity id is defined for testing")
def step_a_test_id_is_defined_for_testing(context, service_name):
    """
    :type context: behave.runner.Context
    """
    context.services[service_name]["id"] = "1234"


@when("I get the entity using the {service_name} api")
def step_i_get_the_entity_using_the_service_api(context, service_name):
    """
    :type context: behave.runner.Context
    :type service_name: str
    """
    service_client = context.services[service_name]["client"]
    context.services[service_name]["resp"] = service_client.get(
        context.services[service_name]["id"]
    )


@when(
    "I get with bad headers in {filename} the entity using the {service_name} api"
)
def step_i_get_the_entity_using_the_service_api(
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
    context.services[service_name]["resp"] = service_client.get(
        context.services[service_name]["id"], headers=headers
    )


@when(
    "I get with parameters in {filename} the entity using the {service_name} api"
)
def step_i_get_the_entity_with_params_in_filename(
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
        resource_id=context.services[service_name]["id"], url_suffix=suffix
    )


@when("I get the status of the entity using the {service_name} api")
def step_i_get_the_status_of_the_entity_using_the_service_api(
    context, service_name
):
    """
    :type context: behave.runner.Context
    :type service_name: str
    """
    service_client = context.services[service_name]["client"]
    context.services[service_name]["resp"] = service_client.get(
        context.services[service_name]["id"], url_suffix="status"
    )


@when(
    "I get the {tasks_service_name} tasks of the entity using the {service_name} api"
)
def step_i_get_the_tasks_of_the_entity_using_the_service_api(
    context, tasks_service_name, service_name
):
    """
    :type context: behave.runner.Context
    :type service_name: str
    """
    service_client = context.services[service_name]["client"]
    context.services[tasks_service_name]["resp"] = service_client.get(
        context.services[service_name]["id"], url_suffix="tasks"
    )


@when(
    "I get a task from the {service_name} entity using the {tasks_service_name} api"
)
def step_i_get_a_task_from_the_entity_using_the_service_api(
    context, service_name, tasks_service_name
):
    """
    :type context: behave.runner.Context
    :type service_name: str
    """
    service_client = context.services[service_name]["client"]
    tasks_service_client = context.services[tasks_service_name]["client"]
    tasks_resp = context.services[tasks_service_name]["resp"]

    first_task = tasks_resp.json()["tasks"][0]
    # TODO config value?
    task_id = first_task["task_id"]
    context.services[tasks_service_name]["id"] = task_id
    context.services[tasks_service_name]["resp"] = tasks_service_client.get(
        resource_id=task_id
    )


@when(
    "I get with bad headers in {filename} a task from the {service_name} entity using the {tasks_service_name} api"
)
def step_i_get_a_task_from_the_entity_using_the_service_api(
    context, service_name, tasks_service_name, filename
):
    """
    :type context: behave.runner.Context
    :type service_name: str
    :type tasks_service_name: str
    :type filename: str
    """
    location = context.json_location
    headers = read_json_from_file(filename, location)

    service_client = context.services[service_name]["client"]
    tasks_service_client = context.services[tasks_service_name]["client"]
    tasks_resp = context.services[tasks_service_name]["resp"]

    first_task = tasks_resp.json()["tasks"][0]
    # TODO config value?
    task_id = first_task["task_id"]
    context.services[tasks_service_name]["id"] = task_id
    context.services[tasks_service_name]["resp"] = tasks_service_client.get(
        resource_id=task_id, headers=headers
    )


@when(
    "I get a task by id from the {service_name} entity using the {tasks_service_name} api"
)
def step_i_get_a_task_by_id_from_the_entity_using_the_service_api(
    context, service_name, tasks_service_name
):
    """
    :type context: behave.runner.Context
    :type service_name: str
    """
    tasks_service_client = context.services[tasks_service_name]["client"]

    task_id = context.services[tasks_service_name]["id"]
    context.services[tasks_service_name]["resp"] = tasks_service_client.get(
        resource_id=task_id
    )


@step("the {service_name} response contains valid single entity details")
def step_the_service_response_contains_valid_single_entity_details(
    context, service_name
):
    """
    :type context: behave.runner.Context
    :type service_name: str
    """
    service_resp = context.services[service_name]["resp"]
    service_entity = service_resp.json()
    context.check.assertIsInstance(service_entity, dict)
    expected_id = context.services[service_name]["id"]
    actual_id = service_entity.get(get_entity_id_field(service_name))
    context.check.assertEqual(actual_id, expected_id)
    # TODO: validate actual content of entity
    # TODO: need to be able to tell what the entity is, in some
    # tests it's a job, some it's a task, some it's a computer


@step("the {service_name} response contains valid single entity status details")
def step_the_service_response_contains_valid_single_entity_status_details(
    context, service_name
):
    """
    :type context: behave.runner.Context
    :type service_name: str
    """
    service_resp = context.services[service_name]["resp"]
    service_entity = service_resp.json()
    context.check.assertIsInstance(service_entity, dict)
    # TODO: validate actual content of entity


@step("I have a {invalid_id} for {tasks_service_name}")
def step_have_invalid_id(context, invalid_id, tasks_service_name):
    """
    :type context: behave.runner.context
    :type invalid_id: str
    :type tasks_service_name: str
    """
    context.services[tasks_service_name]["id"] = invalid_id
