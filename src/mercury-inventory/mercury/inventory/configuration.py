from mercury.common.configuration import get_configuration


__all__ = ['INVENTORY_CONFIG_FILE', 'inventory_configuration']

INVENTORY_CONFIG_FILE = 'mercury_inventory.yaml'
inventory_configuration = get_configuration(INVENTORY_CONFIG_FILE)