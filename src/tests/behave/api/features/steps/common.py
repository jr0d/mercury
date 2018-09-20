from collections import defaultdict

from behave import given, then, when, step, use_step_matcher

from src.tests.behave.api.features.common.utils import (
    check_params_applied_in_resp
)
from src.tests.behave.api.features.client import APIClient


use_step_matcher("parse")


@given("the account is an {auth} tenant")
def step_the_account_is_an_auth_tenant(context, auth):
    """
    :type context: behave.runner.Context
    :type auth: str
    """
    context.authorized = True
    if auth == "unauthorized":
        context.authorized = False


@given("the auth token for the {service_name} client is nonexistent")
def step_the_auth_token_is_nonexistent(context, service_name):
    """
    :type context: behave.runner.Context
    :type service_name: str
    """
    client = context.services[service_name]["client"]
    client.headers.pop("X-Auth-Token")


@given("a {service_name} bad url {bad_url} is provided")
def step_a_service_bad_url_is_provided(context, service_name, bad_url):
    """
    : type context: behave.runner.Context
    : type service_name: str
    : type bad_url: str
    """
    request_kwargs = dict()
    request_kwargs["timeout"] = None
    request_kwargs["ssl_certificate_verify"] = False
    request_kwargs["verbose"] = True

    client_kwargs = dict()
    client_kwargs["authorized"] = context.authorized

    context.services[service_name]["name"] = service_name

    full_service_url = context.base_url + bad_url
    context.services[service_name]["url"] = full_service_url
    context.services[service_name]["client"] = APIClient(
        base_url=full_service_url,
        request_kwargs=request_kwargs,
        client_kwargs=client_kwargs,
    )


@given("the {service_name} client URL is {service_url}")
def step_the_service_client_url_is(context, service_name, service_url):
    """
    :type context: behave.runner.Context
    :type service_name: str
    :type service_url: str
    """
    request_kwargs = dict()
    request_kwargs["timeout"] = None
    request_kwargs["ssl_certificate_verify"] = False
    request_kwargs["verbose"] = True

    client_kwargs = dict()
    client_kwargs["authorized"] = context.authorized

    # Keep track of services being used
    context.services[service_name] = defaultdict(dict)
    context.services[service_name]["name"] = service_name

    # Construct complex urls
    if "_id>" in service_url:
        new_url_parts = service_url.split("/")
        url_parts = service_url.split("/")
        for index, element in enumerate(url_parts):
            # note:  all feature files will have to conform to using
            # *_id> in any url passed in for service entity ids
            # ex: /loadbalancers/<lb_id>/nodes/<node_id>
            if "_id>" in element:
                service_url_part = url_parts[index - 1]
                new_url_parts[index] = context.services[service_url_part]["id"]
        service_url = "/".join(new_url_parts)

    full_service_url = context.base_url + service_url
    context.services[service_name]["url"] = full_service_url
    context.services[service_name]["client"] = APIClient(
        base_url=full_service_url,
        request_kwargs=request_kwargs,
        client_kwargs=client_kwargs,
    )


@then("the {service_name} response status is {status_code} {reason}")
def step_the_service_response_status_is(
    context, service_name, status_code, reason
):
    """
    :type context: behave.runner.Context
    :type service_name: str
    :type status_code: str
    :type reason: str
    """
    context.check.assertEqual(
        context.services[service_name]["resp"].status_code,
        int(status_code),
        msg="Response status code was {}, should be {}".format(
            context.services[service_name]["resp"], status_code
        ),
    )

    actual_resp_reason = context.services[service_name]["resp"].reason
    context.check.assertEqual(
        actual_resp_reason.upper(),
        reason.upper(),
        msg="Response reason was {}, should be {}".format(
            actual_resp_reason, reason
        ),
    )


@step("the {service_name} response contains an error message of")
def step_the_service_response_contains_an_error_message_of(
    context, service_name
):
    """
    :type context: behave.runner.Context
    :type service_name: str
    """
    # replace line breaks with double space in expected message
    expected_error_message = context.text.replace("\r", "  ").replace(
        "\n", "  "
    )
    actual_error_message = context.services[service_name]["resp"].json()[
        "message"
    ]
    context.check.assertEqual(
        actual_error_message,
        expected_error_message,
        msg="Response message was {}, should be {}".format(
            actual_error_message, expected_error_message
        ),
    )


@step("a {service_name} {invalid_id} is provided")
def step_a_service_invalid_id_is_provided(context, service_name, invalid_id):
    """
    :type context: behave.runner.Context
    :type service_name: str
    :type invalid_id: str
    """
    context.services[service_name]["id"] = invalid_id


@then("url parameters to the {service_name} api are applied")
def step_url_parameters_to_service_api_are_applied(context, service_name):
    """
    :type context: behave.runner.Context
    :type service_name: str
    """

    resp = context.services[service_name]["resp"]
    param_data = context.services[service_name]["param_data"]
    params_applied = check_params_applied_in_resp(param_data, resp)

    context.check.assertTrue(params_applied)


@then("the valid url parameters to the {service_name} api are applied")
def step_valid_url_parameters_to_service_api_are_applied(context, service_name):
    """
    :type context: behave.runner.Context
    :type service_name: str
    """

    resp = context.services[service_name]["resp"]
    param_data = context.services[service_name]["param_data"]
    keys = param_data.keys()

    # Check each url parameter
    # If null was passed as a url param, ignore it
    # Remove any invalid projection keys so we don't check for step_i_get_the_list_of_service
    # Since they are ignored when the query is passed to mongo
    for key in keys:
        if param_data[key] == None:
            break
        if key == "projection":
            p = param_data[key].split(",")
            p = [projection for projection in p if "invalid" not in projection]
            for projection in p:
                if "invalid" in projection:
                    p.remove(projection)
            param_data[key] = ",".join(p)
    # Check that all the (valid) url parameters are applied properly
    params_applied = check_params_applied_in_resp(param_data, resp)
    context.check.assertTrue(params_applied)


# Used for bad method testing
@when("I use {method} on {service_name}")
def step_i_use_method_on_service(context, method, service_name):
    """
    :type context: behave.runner.Context
    :type method: str
    :type service_name: str
    """
    service_client = context.services[service_name]["client"]
    if method == "get":
        context.services[service_name]["resp"] = service_client.get()
    elif method == "post":
        context.services[service_name]["resp"] = service_client.post(data={})
    # TODO etc


# Used for bad method testing
@when("I with an entity use {method} on {service_name}")
def step_i_use_method_on_service_with_entity(context, method, service_name):
    """
    :type context: behave.runner.Context
    :type method: str
    :type service_name: str
    """
    service_client = context.services[service_name]["client"]
    if method == "get":
        context.services[service_name]["resp"] = service_client.get(
            context.services[service_name]["id"]
        )
    elif method == "post":
        context.services[service_name]["resp"] = service_client.post(
            data={}, resource_id=context.services[service_name]["id"]
        )
