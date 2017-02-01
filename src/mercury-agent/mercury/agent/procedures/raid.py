import logging

from mercury.agent.capabilities import capability
from mercury.agent.configuration import get_inventory_client
from mercury.hardware.drivers.drivers import get_subsystem_drivers
from mercury.inspector.inspect import global_device_info
from mercury.inspector.inspectors.raid import raid_inspector

log = logging.getLevelName(__name__)


def has_abstraction_handler():
    raid_drivers = get_subsystem_drivers('raid')
    for driver in raid_drivers:
        if hasattr(driver, 'raid_abstraction_handler'):
            return True
    return False


def update_inventory():
    inventory_client = get_inventory_client()
    raid_info = raid_inspector(global_device_info)
    mercury_id = global_device_info['mercury_id']

    log.debug('RAID configuration changed, updating inventory')
    inventory_client.update_one(mercury_id, {'raid': raid_info})


def update_on_change(f):
    def wrapped_f(*args, **kwargs):
        result = f(*args, **kwargs)
        update_inventory()
        return result
    wrapped_f.__name__ = f.__name__
    wrapped_f.__doc__ = f.__doc__
    return wrapped_f


@capability('create_logical_volume',
            description='Create a logical volume',
            kwarg_names=['adapter', 'level'],
            serial=True,
            dependency_callback=has_abstraction_handler,
            timeout=120
            )
@update_on_change
def create_logical_drive(adapter, level, drives=None, size=None, array=None):
    """

    :param adapter:
    :param level:
    :param drives:
    :param size:
    :param array:
    :return:
    """

