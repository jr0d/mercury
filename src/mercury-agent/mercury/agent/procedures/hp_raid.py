# Copyright 2015 Jared Rodriguez (jared.rodriguez@rackspace.com)
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import logging

from mercury.agent.capabilities import capability
from mercury.agent.backend_client import get_backend_client
from mercury.common.exceptions import MercuryUserError
from mercury.hardware.drivers.drivers import driver_class_cache
from mercury.inspector.inspect import global_device_info
from mercury.inspector.inspectors.raid import raid_inspector


log = logging.getLogger(__name__)


def get_hp_raid_driver():
    hp_raid_driver = driver_class_cache.get('hpssa')
    if not hp_raid_driver:
        # Once dependent capabilities are added, this will no longer be necessary
        log.error('Attempt to use platform specific procedure without supporting driver')
        raise MercuryUserError('Required driver, hpssa, is not loaded. Check platform')
    return hp_raid_driver


def has_hp_raid_driver():
    return bool(driver_class_cache.get('hpssa'))


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


@capability('hpssa_create_array',
            description='Create array on an HP SmartArray Controller',
            kwarg_names=['slot', 'selection', 'raid'],
            serial=True,
            dependency_callback=has_hp_raid_driver,
            timeout=120
            )
@update_on_change
def hpssa_create_array(slot, selection, raid, array_letter=None, array_type='ld', size='max',
                       stripe_size='default', write_policy='writeback', sectors=32, caching=True,
                       data_ld=None, parity_init_method='default'):
    """
    Create an array

    :param slot: Slot ID of the adapter you are targeting
    :param selection: all, allunassigned, Port:Box:Bay,...  , 1I:1:1-1I:1:6
    :param raid: 0, 1, 5, 6, 1+0, 1+0asm, 50, 60
    :param array_letter: Optional array ID, Any unused, A-Z
    :param array_type: ld, ldcache, arrayr0
    :param size: size in MB, min, max, maxmbr
    :param stripe_size: 2**3-10 (8-1024), default
    :param write_policy: writeback, writethrough
    :param sectors: 32, 64
    :param caching: True | False
    :param data_ld: ld ID, required if array_type == ldcache
    :param parity_init_method: default

    :return type dict: stdout, stderr, returncode
    """

    hp_raid_driver = get_hp_raid_driver()

    log.info('Creating HPSSA Array: {0} {1} {2}'.format(slot, str(selection), raid))

    result = hp_raid_driver.handler.hpssa.create(
        slot,
        selection,
        raid,
        array_letter=array_letter,
        array_type=array_type,
        size=size,
        stripe_size=stripe_size,
        write_policy=write_policy,
        sectors=sectors,
        caching=caching,
        data_ld=data_ld,
        parity_init_method=parity_init_method
    )

    if result.returncode:
        log.error('Error creating array')
        raise MemoryError('Failed to create array: stdout={0}\nstderr={1}'.format(result,
                                                                                  result.stderr))

    return {'stdout': result, 'stderr': result.stderr, 'returncode': result.returncode}


@capability('hpssa_delete_ld', description='Delete a logical drive on a given controller',
            kwarg_names=['slot', 'logical_drive'], serial=True,
            dependency_callback=has_hp_raid_driver, timeout=120)
@update_on_change
def hpssa_delete_ld(slot, logical_drive):
    """
    Delete a logical drive
    :param slot: Adapter slot
    :param logical_drive: Logical drive id
    :return dict: stdout, stderr, returncode
    """
    hp_raid_driver = get_hp_raid_driver()
    result = hp_raid_driver.handler.hpssa.hpssa.delete_logical_drive(slot, logical_drive)

    return {'stdout': result, 'stderr': result.stderr, 'returncode': result.returncode}


@capability('hpssa_clear_configuration', description='Delete all arrays on a given controller',
            kwarg_names=['slot'], serial=True, dependency_callback=has_hp_raid_driver,
            timeout=120)
@update_on_change
def hpssa_clear_configuration(slot):
    """
    Delete all arrays on a given controller
    :param slot: Adapter slot
    :return dict:  stdout, stderr, returncode
    """
    hp_raid_driver = get_hp_raid_driver()
    result = hp_raid_driver.handler.hpssa.delete_all_logical_drives(slot)

    return {'stdout': result, 'stderr': result.stderr, 'returncode': result.returncode}


@capability('hpssa_clear_configuration_all_controllers',
            description='Delete all configurations from all RAID controllers',
            serial=True,
            dependency_callback=has_hp_raid_driver,
            timeout=120)
@update_on_change
def hpssa_clear_configurations_all_controllers():
    """
    Nuke it from orbit. It's the only way to be sure
    :return dict: Indexed by adapter slot
    """
    hp_raid_driver = get_hp_raid_driver()
    return hp_raid_driver.handler.hpssa.clear_configuration()
