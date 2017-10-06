import logging

from mercury.agent.capabilities import capability
from mercury.agent.backend_client import get_backend_client
from mercury.hardware.drivers.drivers import get_subsystem_drivers
from mercury.hardware.raid.abstraction.api import RAIDActions
from mercury.inspector.inspect import global_device_info
from mercury.inspector.inspectors.raid import raid_inspector

log = logging.getLogger(__name__)


def has_abstraction_handler():
    raid_drivers = get_subsystem_drivers('raid')
    for driver in raid_drivers:
        if isinstance(driver.handler, RAIDActions):
            return True
    return False


def update_inventory():
    backend_client = get_backend_client()
    raid_info = raid_inspector(global_device_info)
    mercury_id = global_device_info['mercury_id']

    log.debug('RAID configuration changed, updating inventory')
    backend_client.update(mercury_id, {'raid': raid_info})


def update_on_change(f):
    def wrapped_f(*args, **kwargs):
        result = f(*args, **kwargs)
        update_inventory()
        return result
    wrapped_f.__name__ = f.__name__
    wrapped_f.__doc__ = f.__doc__
    return wrapped_f


@capability('create_logical_drive',
            description='Creates a logical drive on the specified controller',
            kwarg_names=['adapter', 'level'],
            serial=True,
            dependency_callback=has_abstraction_handler,
            timeout=120
            )
@update_on_change
def abstract_create_logical_drive(adapter, level, drives=None, size=None, array=None):
    """
    :param adapter: Target adapter
    :type adapter: int
    :param level: 0, 1, 5, 6, 10, 1+0, 50, 60
    :type level: str
    :param drives: drives should be referenced as 0 based comma separated indexes, ranges,
        or a combination of both. For example::

            0, 1, 2, 3
                or
            0-3
                or
            0, 2, 4-8, 9, 10

        When using a range, both the lower and upper bounds are inclusive

        Another option is to use all or unassigned. `all` requires that all drives on the
        adapter are not part of the array. `unassigned` will select all drives not currently
        members of an array or participating as spares
    :param size: Size can be specified in bytes (int), a string using SI or IEC standards,
    a percent of total space, or a percent of free space available. If no size is listed,
    all available space will be used
    :param array: An index of an existing array we are updating
    :return:
    """
    log.info('Creating array on adapter {}: level={} drives={} size={} array={}'.format(
        adapter, level, drives, size, array
    ))

    # Right now, I assume that there is only ONE driver type, ie, one vendor type.

    raid_driver = get_subsystem_drivers('raid')[0]

    return raid_driver.handler.create_logical_drive(adapter, level, drives, size, array)


@capability('delete_logical_drive',
            description='Delete the specified logical drive',
            kwarg_names=['adapter', 'array', 'logical_drive'],
            serial=True,
            dependency_callback=has_abstraction_handler,
            timeout=120)
@update_on_change
def abstract_delete_logical_drive(adapter, array, logical_drive):
    """
    :param adapter:
    :param array:
    :param logical_drive:
    :return:
    """
    raid_driver = get_subsystem_drivers('raid')[0]
    return raid_driver.handler.delete_logical_drive(adapter, array, logical_drive)


@capability('clear_configuration',
            description='Clear all arrays from the adapter',
            kwarg_names=['adapter'],
            serial=True,
            dependency_callback=has_abstraction_handler,
            timeout=120)
@update_on_change
def abstract_clear_configuration(adapter):
    """
    :param adapter:
    :return:
    """
    raid_driver = get_subsystem_drivers('raid')[0]
    return raid_driver.handler.clear_configuration(adapter)


@capability('add_spares',
            description='Assign spare drives to the array',
            kwarg_names=['adapter', 'array', 'drives'],
            serial=True,
            dependency_callback=has_abstraction_handler,
            timeout=120)
@update_on_change
def abstract_add_spares(adapter, array, drives):
    """
    :param adapter:
    :param array:
    :param drives:
    :return:
    """
    raid_driver = get_subsystem_drivers('raid')[0]
    return raid_driver.handler.add_spares(adapter, array, drives)
