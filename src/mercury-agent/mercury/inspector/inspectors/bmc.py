import logging


from mercury.hardware.drivers import get_subsystem_drivers
from mercury.inspector.inspectors import expose_late


log = logging.getLogger(__name__)


# noinspection PyUnusedLocal
@expose_late('bmc')
def bmc_inspector(device_info):

    drivers = get_subsystem_drivers('bmc')
    if not drivers:
        return

    if len(drivers) > 1:
        log.warning('Found more than one driver for BMC. This is most likely a bug')

    driver = drivers[0]

    log.info('Running BMC inspector: {}'.format(driver.name))

    return driver.inspect()
