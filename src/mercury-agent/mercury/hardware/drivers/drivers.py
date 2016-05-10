import logging

log = logging.getLogger(__name__)


registered_pci_drivers = list()
driver_class_cache = dict()


class PCIDriverBase(object):
    name = ''
    driver_type = ''
    _handler = None

    def __init__(self):
        self.handler = self._handler()

    @classmethod
    def probe(cls, pci_data):
        """
        Implementations should return a sorted list of PCI devices supported by the handler
        :param pci_data:
        :return:
        """
        raise NotImplementedError

    @classmethod
    def check(cls, pci_device):
        """
        Implementations should check if a PCI device is handled by the driver
        :param pci_device: device_info.pci element
        :return:
        """
        raise NotImplemented

    def inspect(self):
        raise NotImplemented


def driver():
    def decorator(cls):
        log.info('Registering driver: %s' % cls.__name__)
        registered_pci_drivers.append({
            'name': cls.name,
            'class': cls,
            'driver_type': cls.driver_type
        })

        return cls
    return decorator


def get_subsystem_drivers(subsystem):
    drivers = []
    for driver in driver_class_cache:
        if driver_class_cache[driver].driver_type == subsystem:
            drivers.append(driver_class_cache[driver])
    return drivers


def set_driver_cache(driver):
    if not driver_class_cache.get(driver.name):
        log.info('Initializing driver: %s' % driver.name)
        driver_class_cache[driver.name] = driver()

