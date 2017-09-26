import argparse
import json
from pygments import highlight, lexers, formatters
from rax_io import config

from mercury.client.inventory import InventoryComputers
from mercury.client.rpc import ActiveComputers


ac = ActiveComputers(config.MERCURY)


def format_json(data):
    return highlight(json.dumps(data, sort_keys=True, indent=4),
                     lexers.JsonLexer(), formatters.TerminalFormatter())


def jq(data):
    print(format_json(data))


def pause():
    input('=> ')


def demo_capabilities():
    query = {'dmi.sys_vendor': 'HP'}
    to_print = 'create_logical_drive'

    data = ac.query(query, projection=['active.capabilities'])['items'][0]

    jq(data)
    pause()

    capability = data['active']['capabilities'][to_print]
    print(capability['name'])
    print(capability['doc'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Execute mercury commands")
    parser.add_argument('command', help="Command dispatch")

    namespace = parser.parse_args()

    if namespace.command == 'demo_capabilities':
        demo_capabilities()


