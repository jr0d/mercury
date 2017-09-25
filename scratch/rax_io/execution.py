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
    for task in job_query.tasks()['tasks']:
        print('{} : {} , elapsed: {}, message: {}'.format(
            task['mercury_id'][-6:],
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


if __name__ == '__main__':
    execute(config.TARGET_QUERY, 'create_logical_drive', kwargs={
        'adapter': 0,
        'level': '6',
        'drives': 'all'
    })

