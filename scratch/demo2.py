import json


from collections import Counter
from colors import blue, red

from mercury.client.inventory import InventoryComputers
from mercury.client.rpc import ActiveComputers, JobQuery, TaskInterface


from pygments import highlight, lexers, formatters
from size import Size


URL = 'http://mercury.iad3:9005'
TARGETS = {"interfaces.lldp.switch_name": {"$regex": ".*g13.*iad3$"}}

INV = InventoryComputers(URL)
ACTIVE = ActiveComputers(URL)
TASKS = TaskInterface(URL)

# TARGETS = {"raid.adapter_handler": 'hpssa'}


class InventoryResponse(object):
    def __init__(self, response):
        self.items = response.get['items']
        self.count = response.get('total')
        self.limit = response.get('limit')


def prune_inactive(inv_matches, active_matches):
    pruned = []
    for active in active_matches:
        for inv in inv_matches:
            if active['mercury_id'] == inv['mercury_id']:
                pruned.append(inv)
                break

    return pruned


def storage_homogeny_report(report_items):
    counters = [Counter([x['total_drives'] for x in report_items]),
                Counter([x['slot'] for x in report_items]),
                Counter([x['total_size'] for x in report_items])]

    total_items = float(len(report_items))
    v_matrix = []
    for idx in range(len(counters)):
        h_counter = 0
        for value in counters[idx]:
            h_counter = abs(counters[idx][value] / total_items - h_counter)
        v_matrix.append(h_counter)

    return round(sum(v_matrix) / 3, 2)


def _jq(data):
    return highlight(json.dumps(data, sort_keys=True, indent=4),
                     lexers.JsonLexer(), formatters.TerminalFormatter())


def jq(data):
    print(_jq(data))


def bb(message):
    print(blue(message, bg='black'))


def pause():
    input(blue('=> ', bg='black'))


def storage_report():
    active_matches = ACTIVE.query(TARGETS, params={'projection': 'mercury_id'})['active']
    inv_matches = INV.query(TARGETS,
                            params={'projection': 'mercury_id,raid.total_drives,raid.slot,raid.total_size',
                                    'limit': 1000})['items']

    matches = prune_inactive(inv_matches, active_matches)

    report_items = []
    for inv in matches:
        item = {
            'mercury_id': inv['mercury_id'],
            'total_drives': inv['raid'][0]['total_drives'],
            'total_size': Size(inv['raid'][0]['total_size']).humanize,
            'slot': inv['raid'][0]['slot']
        }

        report_items.append(item)

    report = {
        'count': len(matches),
        'items':  report_items,
        'homogeneity': storage_homogeny_report(report_items)
    }

    return report


def hpssa_clear_configuration(slot):
    return {
            'method': 'hpssa_clear_configuration',
            'kwargs': {
                'slot': slot
            }
        }


def hp_create_array(slot, selection, raid):
    return {

            'method': 'hpssa_create_array',
            'kwargs': {
                'slot': slot,
                'selection': selection,
                'raid': raid
            }
        }


def poll_status(timeout=120):
    pass


def active_demo():
    bb('<------- ACTIVE INVENTORY DEMO ------>')
    pause()
    response = ACTIVE.get()

    jq(response)

    pause()


def inventory_demo():
    bb('------> Inventory DEMO <------')
    bb('Query #1: {}, limit: 10')

    pause()

    response = INV.query({}, params={'limit': 10})

    jq(response)

    pause()

    bb('Query #2:  {"interfaces.lldp.switch_name": {"$regex": "g13.*iad3$"}}\n'
       'Limit 10\n'
       'Projection: dmi.product_name,cpu.model_name')

    pause()
    response = INV.query(TARGETS, params={'projection': 'dmi.product_name,cpu.model_name',
                                          'limit': 10})
    jq(response)

    m_id = input('Enter MercuryID => ')
    bb('GET: /api/inventory/computers/{}'.format(m_id))
    pause()
    response = INV.get(m_id)

    jq(response)

    pause()


def capabilities_demo():
    bb('<------- CAPABILITIES DEMO ------>')
    m_id = input('Enter MercuryID => ')
    bb('GET: /api/active/computers/{}'.format(m_id))
    pause()
    response = ACTIVE.get(m_id)

    jq(response)
    pause()

    # for c in response.get('capabilities').values():
    #     print('{}\n{}\n{}'.format(red(bold(c['name'])),
    #                               blue(c['description']),
    #                               c.get('doc') and magenta(c['doc'] or '')))
    #
    # pause()


def rpc_demo():
    bb('<---- RPC DEMO ---->')
    bb('Task #1: Hello World on target: {}')
    job = JobQuery(URL, {}, instruction={'method': 'echo', 'args': ['Hello World!']})
    pause()
    job.post_job()
    bb('JobID: {}'.format(job.job_id))
    pause()
    jq(job.get_status())
    pause()

    bb('Task #2: method: run, args: [cat /etc/shadow] : target {}')
    job = JobQuery(URL, {}, instruction={'method': 'run', 'args': ['cat /etc/shadow']})
    pause()
    job.post_job()
    bb('JobID: {}'.format(job.job_id))
    pause()
    jq(job.get_status())
    bb('Show task results...')
    pause()
    task = TaskInterface(URL)
    jq(task.get(job.job_id))
    pause()
    print(red('PWNED by Mercury', style='bold+underline', bg='yellow'))
    pause()


def storage_demo():
    bb('<---- STORAGE DEMO ---->')
    bb('Storage Report Aggregator\nQ: {"interfaces.lldp.switch_name": {"$regex": ".*g13.*iad3$"}}')
    pause()
    jq(storage_report())

    pause()

    bb('Task #1: Delete configuration from controller in slot 3\n'
       'Instruction: hpssa_clear_configuration\n'
       'kwargs: {slot: 3}\n'
       'Targets: {"interfaces.lldp.switch_name": {"$regex": ".*g13.*iad3$"}}')
    pause()
    job = JobQuery(URL, TARGETS, hpssa_clear_configuration(3))
    job.post_job()
    bb('JobID: {}'.format(job.job_id))
    pause()
    jq(job.get_status())
    bb('Show task results...')
    pause()
    task = TaskInterface(URL)
    jq(task.get(job.job_id))

    m_id = input('Enter MercuryID => ')
    bb('GET: /api/inventory/computers/{}'.format(m_id))
    pause()
    response = INV.get(m_id, params={'projection': 'raid.configuration'})

    jq(response)
    pause()

    bb('Task #2: Create Array\n'
       'Instruction: hpssa_create_array\n'
       'kwargs: {slot: 3, selection: all, raid: 6}\n'
       'Targets: {"interfaces.lldp.switch_name": {"$regex": ".*g13.*iad3$"}}')

    pause()
    job = JobQuery(URL, TARGETS, hp_create_array(3, 'all', '6'))
    job.post_job()
    bb('JobID: {}'.format(job.job_id))
    pause()
    jq(job.get_status())
    bb('Show task results...')
    pause()
    task = TaskInterface(URL)
    jq(task.get(job.job_id))

    m_id = input('Enter MercuryID => ')
    bb('GET: /api/inventory/computers/{}'.format(m_id))
    pause()
    response = INV.get(m_id, params={'projection': 'raid.configuration'})

    jq(response)

    pause()


def provisioning_demo():
    import yaml

    with open('ubuntu.yaml') as fp:
       data = yaml.load(fp)

    jq(data)
    pause()

    j = JobQuery(URL, {'mercury_id': '0158e25529ef2757e621507069bc4301a605237873'}, instruction={
       'method': 'press',
       'kwargs': {
           'configuration': data
       }

    })

    j.post_job()

    bb('JOB ID: {}'.format(j.job_id))

    pause()

    jq(j.get_status())
    bb('Show task results...')
    pause()
    task = TaskInterface(URL)
    jq(task.get(j.job_id))


if __name__ == '__main__':
    bb('Mercury Demo v1')

#    import sys
#    provisioning_demo()
#    sys.exit()

    pause()
    # INVENTORY DEMO

    inventory_demo()

    # ACTIVE INVENTORY DEMO

    active_demo()

    # CAPABILITIES DEMO

    capabilities_demo()

    # RPC DEMO

    rpc_demo()

    # STORAGE DEMO

    storage_demo()

    # PROVISIONING DEMO

    provisioning_demo()
