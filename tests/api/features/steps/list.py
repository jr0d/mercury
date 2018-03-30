import random

from behave import when, step, then, given


@when("I get the list of {service_name}")
def step_i_get_the_list_of_service(context, service_name):
    """
    :type context: behave.runner.Context
    :type service_name: str
    """
    service_client = context.services[service_name]['client']
    context.services[service_name]['resp'] = service_client.get()


@step("the response contains a list of {service_name}")
def step_the_response_contains_a_list_of_service_ids(
        context, service_name):
    """
    :type context: behave.runner.Context
    :type service_name: str
    """
    service_resp = context.services[service_name]['resp']
    listed_service_names = context.cfg.MERCURY.listed_service_names
    listed_service_names = listed_service_names.split(', ')
    # TODO
    # Better configuration for these strings
    if service_name in listed_service_names:
        service_entities = service_resp.json()['items']
    elif service_name == "rpc_jobs":
        service_entities = service_resp.json()['jobs']
    elif service_name == "rpc_tasks":
        service_entities = service_resp.json()['tasks']
    context.check.assertIsInstance(service_entities, list)
    # TODO make sure the actual entities in the list are what they should be
    # WIP: Validate for service IDs


@then("the entity is {existence} in the {service_name} list")
def step_the_entity_is_exists_in_the_service_list(context, existence,
                                                  service_name):
    """
    :type context: behave.runner.Context
    :param existence: can either be 'found' or 'not found'
    :type existence: str
    :type service_name: str
    """
    device_id = context.services[service_name]['id']
    entities = context.services[service_name]['resp'].json()[service_name]
    if existence == 'not found':
        context.check.assertNotIn(device_id,
                                  [entity.id for entity in entities])
    elif existence == 'found':
        context.check.assertIn(device_id, [entity.id for entity in entities])
    else:
        raise Exception("{} is not a valid existence name!  "
                        "Please use 'found' or 'not found'")
