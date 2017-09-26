from mercury.client.rpc import ActiveComputers
from rax_io import config

active_api = ActiveComputers(config.MERCURY)

HOSTNAME_TEMPLATE = 'demo{}.iad3.kir.kickstart.rackspace.com'


def generate_assets_for_targets(targets):
    assets = {}
    inventory = active_api.query(targets, projection=['interfaces'])
    cnt = 1
    for computer in inventory['items']:
        data = {}
        for interface in computer['interfaces']:
            if interface['address_info']:
                data['ip_address'] = interface['address_info'][0]['addr']
        data['hostname'] = HOSTNAME_TEMPLATE.format(cnt)
        assets[computer['mercury_id']] = data
        cnt += 1
    return assets


if __name__ == '__main__':
    from pprint import pprint
    pprint(generate_assets_for_targets())
