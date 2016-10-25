import json

from collections import Counter

from mercury.client.inventory import InventoryComputers
from mercury.client.rpc import ActiveComputers, JobQuery

from pprint import pprint
from pygments import highlight, lexers, formatters
from size import Size

INV = InventoryComputers('http://mercury.iad3:9005')
ACTIVE = ActiveComputers('http://mercury.iad3:9005')
TARGETS = {"interfaces.lldp.switch_name": {"$regex": ".*g13.*iad3$"}}
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


def storage_homogony_report(report_items):
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


def storage_report():
    active_matches = ACTIVE.query(TARGETS, params={'projection': 'mercury_id'})['active']
    inv_matches = INV.query(TARGETS,
                            params={'projection': 'mercury_id,raid.total_drives,raid.slot,raid.total_size',
                                    'limit': 1000})['items']

    matches = prune_inactive(inv_matches, active_matches)

    report = {}
    report_items = []
    for inv in matches:
        item = {
            'mercury_id': inv['mercury_id'],
            'total_drives': inv['raid'][0]['total_drives'],
            'total_size': Size(inv['raid'][0]['total_size']).humanize,
            'slot': inv['raid'][0]['slot']
        }

        report_items.append(item)

    print(highlight(json.dumps(dict(report=report_items), sort_keys=True, indent=4),
                    lexers.JsonLexer(), formatters.TerminalFormatter()))

    print(storage_homogony_report(report_items))

if __name__ == '__main__':
    storage_report()
