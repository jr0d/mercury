from collections import defaultdict

from behave import given, then, step, use_step_matcher

from tests.api.features.client import APIClient


use_step_matcher("parse")


@given('the account is an {auth} tenant')
def step_the_account_is_an_auth_tenant(context, auth):
    """
    :type context: behave.runner.Context
    :type auth: str
    """
    # TODO: Temporary until identity system is in place
    context.bypass_auth = True
    if auth == "unauthorized":
        context.bypass_auth = False


@given("the {service_name} client URL is {service_url}")
def step_the_service_client_url_is(context, service_name, service_url):
    """
    :type context: behave.runner.Context
    :type service_name: str
    :type service_url: str
    """
    request_kwargs = dict()
    request_kwargs['timeout'] = None
    request_kwargs['ssl_certificate_verify'] = False
    request_kwargs['verbose'] = True
    request_kwargs['bypass_auth'] = context.bypass_auth

    # Keep track of services being used
    context.services[service_name] = defaultdict(dict)
    context.services[service_name]['name'] = service_name

    # Construct complex urls
    if "_id>" in service_url:
        new_url_parts = service_url.split('/')
        url_parts = service_url.split('/')
        for index, element in enumerate(url_parts):
            # note:  all feature files will have to conform to using
            # *_id> in any url passed in for service entity ids
            # ex: /loadbalancers/<lb_id>/nodes/<node_id>
            if "_id>" in element:
                service_url_part = url_parts[index - 1]
                new_url_parts[index] = (
                    context.services[service_url_part]['id'])
        service_url = '/'.join(new_url_parts)

    full_service_url = context.base_url + service_url
    context.services[service_name]['url'] = full_service_url
    context.services[service_name]['client'] = APIClient(
        base_url=full_service_url, request_kwargs=request_kwargs)


@then("the {service_name} response status is {status_code} {reason}")
def step_the_service_response_status_is(context, service_name, status_code,
                                        reason):
    """
    :type context: behave.runner.Context
    :type service_name: str
    :type status_code: str
    :type reason: str
    """
    context.check.assertEqual(
        context.services[service_name]['resp'].status_code,
        int(status_code),
        msg="Response status code was {}, should be {}".format(
            context.services[service_name]['resp'], status_code))

    actual_resp_reason = context.services[service_name]['resp'].reason
    context.check.assertEqual(
        actual_resp_reason.upper(),
        reason.upper(),
        msg="Response reason was {}, should be {}".format(
            actual_resp_reason, reason))


@step("the {service_name} response contains an error message of")
def step_the_service_response_contains_an_error_message_of(
        context, service_name):
    """
    :type context: behave.runner.Context
    :type service_name: str
    """
    # replace line breaks with double space in expected message
    expected_error_message = context.text.replace('\r', '  ').replace(
        '\n', '  ')
    actual_error_message = (
        context.services[service_name]['resp'].json()['message'])
    context.check.assertEqual(
        actual_error_message,
        expected_error_message,
        msg="Response message was {}, should be {}".format(
            actual_error_message, expected_error_message))


@step("a {service_name} {invalid_id} is provided")
def step_a_service_invalid_id_is_provided(context, service_name, invalid_id):
    """
    :type context: behave.runner.Context
    :type service_name: str
    :type invalid_id: str
    """
    context.services[service_name]['id'] = invalid_id
