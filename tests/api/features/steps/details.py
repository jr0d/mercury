from behave import when, step


@step("a {service_name} entity id is located for testing")
def step_a_service_id_is_located_for_testing(context, service_name):
    """
    :type context: behave.runner.Context
    :type service_name: str
    """
    # Find a valid service entity from list call
    context.services[service_name]['id'] = None
    service_client = context.services[service_name]['client']
    response = service_client.get()
    try:
        entity_id = response.json()['items'][0]['mercury_id']
        context.services[service_name]['id'] = entity_id
    except IndexError:
        context.check.assertIsNotNone(
            context.services[service_name]['id'],
            msg='WIP: Create {} API Not Yet Implemented'.format(service_name))
        # WIP: Create new service entity since we don't have any


@when("I get the entity using the {service_name} api")
def step_i_get_the_entity_using_the_service_api(context, service_name):
    """
    :type context: behave.runner.Context
    :type service_name: str
    """
    service_client = context.services[service_name]['client']
    context.services[service_name]['resp'] = service_client.get(
        context.services[service_name]['id'])


@step("the {service_name} response contains valid single entity details")
def step_the_service_response_contains_valid_single_entity_details(
        context, service_name):
    """
    :type context: behave.runner.Context
    :type service_name: str
    """
    service_resp = context.services[service_name]['resp']
    service_entity = service_resp.json()
    context.check.assertIsInstance(service_entity, dict)
    # WIP validate service entity details
