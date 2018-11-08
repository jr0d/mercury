import re
import json
import time
import operator
from functools import reduce

from behave import given, then, when, step, use_step_matcher
from src.tests.behave.api.features.common.utils import read_json_from_file


@then(
    "the first {service_name} task for the {device_service} device has the stdout output contained in {out_filename}"
)
def step_the_first_task_has_stdout_output_in_file(
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
        device_resp = device_client.get(device_id)

        if "_sub_" in stdout:
            # The _sub_ is formated like this _sub_<name_of_data>_sub_
            # The <name_of_data> portion is replaced with the actual value and _sub_ is removed
            # We need to get information from the mercury device details
            # to compare to what was returned from the RPC job

            subs = re.findall("_sub_.*?_sub_", stdout, flags=re.DOTALL)
            for sub in subs:
                keys = sub.replace("_sub_", "").split(".")
                value = reduce(operator.getitem, keys, device_resp.json())
                stdout = stdout.replace(sub, str(value))
            # reduce something like active.rpc_port in order ro read it
            # from a dict, for example resp.json()["active"]["rpc_port"]

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


@then(
    "the first {service_name} task for the {device_service} device has the message output contained in {out_filename}"
)
def step_the_first_task_has_message_output_in_file(
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
        device_id = context.services[device_service]["id"]
        device_resp = device_client.get(device_id)

        task_message_keys = set(task_message.keys())
        device_keys = set(device_resp.json().keys())

        diff = set(
            [item for item in task_message_keys if item not in device_keys]
            + [item for item in device_keys if item not in task_message_keys]
        )
        not_shared = set(
            ["origin", "time_created", "active", "time_updated", "_id"]
        )

        context.check.assertEqual(
            diff, not_shared, msg="Expected keys don't match"
        )

        context.check.assertEqual(
            device_resp.json()["bmc"]["network"]["ip_address"],
            task_message["bmc"]["network"]["ip_address"],
            msg="IP was {}, should be {}".format(
                task_message["bmc"]["network"]["ip_address"],
                device_resp.json()["bmc"]["network"]["ip_address"],
            ),
        )
        # TODO
        # instead of inspector_out.json, have json with list of fields to check
        # similar ot the IP check above
