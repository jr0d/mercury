import json
import time
import operator
from functools import reduce

from behave import given, then, when, step, use_step_matcher
from src.tests.behave.api.features.common.utils import read_json_from_file


@then(
    "the first {service_name} task for the {device_service} device has the output contained in {out_filename}"
)
def step_the_first_task_has_output_in_file(
    context, service_name, out_filename, device_service
):
    """
    :type context: behave.runner.Context
    :type service_name: str
    :type out_filename: str
    """
    service_client = context.services[service_name]["client"]
    device_client = context.services[device_service]["client"]
    location = context.json_location
    data = read_json_from_file(out_filename, location)

    tasks = context.services[service_name]["tasks"]
    first_task = tasks[0]

    task_resp = service_client.get(resource_id=first_task["task_id"])
    task_message = task_resp.json()["message"]

    if data["message"] is None:
        context.check.assertEqual(
            data["message"],
            task_message,
            msg="Message was {}, should be {}".format(
                task_message, data["message"]
            ),
        )
    else:
        stdout = data["message"]["stdout"]
        returncode = data["message"]["returncode"]
        stderr = data["message"]["stderr"]

        device_id = context.services[device_service]["id"]

        if "_sub_" in stdout:
            # We need to get information from the mercury device details
            # to compare to what was returned from the RPC job
            prefix, suffix = stdout.split("_sub_")
            device_resp = device_client.get(device_id)

            # reduce something like active.rpc_port in order ro read it
            # from a dict, for example resp.json()["active"]["rpc_port"]
            keys = prefix.split(".")
            actual_value = reduce(operator.getitem, keys, device_resp.json())
            stdout = actual_value + suffix

        context.check.assertEqual(
            task_message["stdout"],
            stdout,
            msg="Stdout was {}, should be {}".format(
                task_message["stdout"], stdout
            ),
        )
        context.check.assertEqual(
            task_message["returncode"],
            returncode,
            msg="Returncode was {}, should be {}".format(
                task_message["returncode"], returncode
            ),
        )
        context.check.assertEqual(
            task_message["stderr"],
            stderr,
            msg="Stderr was {}, should be {}".format(
                task_message["stderr"], stderr
            ),
        )
