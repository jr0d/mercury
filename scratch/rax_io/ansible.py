from rax_io import active

template = '{ip_address} ansible_ssh_user=root snet_mac_address={mac_address}'


def print_ansible_inventory():
    hosts = active.get_active(projection='interfaces')['items']
    addresses = []
    for host in hosts:
        for interface in host['interfaces']:
            if interface['address_info']:
                print(template.format(**dict(ip_address=interface['address_info'][0]['addr'],
                                             mac_address=interface['address'])))
                break

    for address in addresses:
        print(address)


if __name__ == '__main__':
    print_ansible_inventory()
