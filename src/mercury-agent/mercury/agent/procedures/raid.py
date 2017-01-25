import logging

from mercury.agent.capabilities import capability
from mercury.agent.configuration import get_inventory_client
from mercury.hardware.drivers.drivers import get_subsystem_drivers

log = logging.getLevelName(__name__)


def has_abstraction_handler():
    raid_drivers = get_subsystem_drivers('raid')
    for driver in raid_drivers:
        if driver.raid_abstraction