from collections import defaultdict

from behave import given, then, when, step, use_step_matcher


use_step_matcher("parse")


@given('something with the agent')
def step_something_with_the_agent(context):
    """
    :type context: behave.runner.Context
    """
    pass
