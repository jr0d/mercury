from mercury.client.rpc import ActiveComputers

from rax_io import config

active_client = ActiveComputers(config.MERCURY)


def get_active(projection=None):
    return active_client.get(params={'projection': projection})


if __name__ == '__main__':
    print(get_active(''))
