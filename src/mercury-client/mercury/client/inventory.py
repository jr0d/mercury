from mercury.client.base import InterfaceBase


class InventoryComputers(InterfaceBase):
    SERVICE_URI = 'api/inventory/computers'


if __name__ == '__main__':
    from pprint import pprint
    ic = InventoryComputers('http://localhost:9005')

    pprint(ic.query({}))

