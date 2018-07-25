from collections import defaultdict

from behave import given, then, when, step, use_step_matcher


use_step_matcher("parse")


@given('an agent is running on {ip}')
def step_an_agent_is_running_on_ip(context, ip):
    """
    :type context: behave.runner.Context
    :type ip: str
    """

    pass
