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


@step("the response contains a list of {service_name} on my account")
def step_the_response_contains_a_list_of_service_ids_on_my_account(
        context, service_name):
    """
    :type context: behave.runner.Context
    :type service_name: str
    """
    service_resp = context.services[service_name]['resp']
    # active computers are listed in the "items" field
    service_entities = service_resp.json()['items']
    context.check.assertIsInstance(service_entities, list)
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


@given("I have the page marker of a {service_name} entity")
def step_the_page_marker_of_an_entity(context, service_name):
    """Discover a page marker to use for a pagination tests

    Page markers are entity ids.

    :type context: behave.runner.Context
    :type service_name: str
    """
    # List the resources to find the ID of an entity to use as a page marker
    client = context.services[service_name]['client']
    resp = client.get()

    abort_msg = ('Failed trying to auto-discover the ID of a resource to use '
                 'as a page marker for pagination tests')
    context.check.assertEqual(resp.status_code, 200, abort_msg)
    entities = resp.json()[service_name]

    context.check.assertGreater(len(entities), 0, abort_msg)

    # Choose a random entity ID from the first page of resources
    page_marker = random.choice(entities)['id']

    context.services[service_name]['page_marker'] = page_marker


@when("I get a page of {service_name} using a page marker")
def step_get_a_page_of_entities_using_page_marker(context, service_name):
    """Fetch a page of entities at a page marker

    :type context: behave.runner.Context
    :type service_name: str
    """
    page_marker = context.services[service_name]['page_marker']
    client = context.services[service_name]['client']

    # TODO: A placeholder - exact parameters are unknown right now
    resp = client.get(params={'marker': page_marker})
    context.services[service_name]['resp'] = resp
    context.services[service_name]['pages'] = [resp]


@when('I list {service_name} using a page size of {supplied_page_size}')
def step_list_entities_using_page_size(context, service_name,
                                       supplied_page_size):
    """List pages of a given size

    :type context: behave.runner.Context
    :type service_name: str
    :param supplied_page_size: The user-supplied page size to test with
    :type supplied_page_size: str (containing an integer)
    """
    client = context.services[service_name]['client']

    # TODO: A placeholder - exact parameters are unknown right now
    resp = client.get(params={'limit': supplied_page_size})
    context.services[service_name]['resp'] = resp
    context.services[service_name]['pages'] = [resp]


@then(
    'the size of each page of {service_name} is at most {expected_page_size}'
)
def step_size_of_each_page_is_at_most(context, service_name,
                                      expected_page_size):
    """Checks the size of each page in a paginatied list response

    :type context: behave.runner.Context
    :type service_name: str
    :param supplied_page_size: The user-supplied page size to test with
    :type supplied_page_size: str (containing an integer)
    """
    if expected_page_size == 'the max page size':
        # TODO: This must match the API's default max page size
        expected_page_size = 100

    pages = context.services[service_name]['pages']
    for resp in pages:
        context.check.assertLessEqual(
            len(resp.json()[service_name]), int(expected_page_size)
        )


@then('the page of {service_name} starts at the page marker')
def step_the_page_starts_at_the_page_marker(context, service_name):
    """Checks the size of each page in a paginatied list response

    :type context: behave.runner.Context
    :type service_name: str
    :param supplied_page_size: The user-supplied page size to test with
    :type supplied_page_size: str (containing an integer)
    """
    page_marker = context.services[service_name]['page_marker']
    pages = context.services[service_name]['pages']

    resp = pages[0]
    entities = resp.json()[service_name]
    context.check.assertEqual(entities[0]['id'], page_marker)
