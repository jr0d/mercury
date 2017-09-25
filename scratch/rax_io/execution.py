import os
import argparse
import curses
import json
import time
import yaml

from mercury.client import rpc

from rax_io import config


def poll_tasks(job_query, interval=0.5):
    def draw(window):
        start_time = time.time()
        while not job_query.status()['time_completed']:
            window.clear()
            count = 0
            for task in job_query.tasks()['tasks']:
                if task['time_completed']:
                    update_time = int(task['time_completed'] - task['time_started'])
                else:
                    update_time = int(time.time() - start_time)
                window.addstr(
                    count, 0, '{} : {} , Action: {}, elapsed: {}'.format(
                        task['mercury_id'][-6:],
                        task['task_id'],
                        task['action'],
                        update_time))
                count += 1
            window.refresh()
            time.sleep(interval)
    curses.wrapper(draw)
    print('Job ID: {}\n'.format(job_query.job_id))
    for task in job_query.tasks()['tasks']:
        print('{} , elapsed: {}, message: {}'.format(
            task['task_id'],
            int(task['time_completed'] - task['time_started']),
            task['message'],

        ))


def _exec(target, instruction):
    jq = rpc.JobQuery(config.MERCURY, target, instruction)
    jq.post_job()
    poll_tasks(jq)


def execute(target, method, args=None, kwargs=None):
    instruction = {
        'method': method,
        'args': args or [],
        'kwargs': kwargs or {}
    }
    jq = rpc.JobQuery(config.MERCURY, target, instruction)
    jq.post_job()
    poll_tasks(jq)


def preprocessor_exec(target, instruction):
    _exec(target, instruction)


def configuration_from_yaml(path):
    with open(path) as fp:
        return yaml.load(fp)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Execute mercury commands")
    parser.add_argument('query', help="The target query")
    parser.add_argument('instruction', help='Path to the instruction JSON')

    namespace = parser.parse_args()

    if os.path.isfile(namespace.instruction):
        with open(namespace.instruction) as fp:
            _instruction = json.load(fp)
    else:
        _instruction = json.loads(namespace.instruction)

    _target = json.loads(namespace.query)

    _exec(_target, _instruction)
