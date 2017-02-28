import logging

log = logging.getLogger(__name__)


registered_drivers = list()
driver_class_cache = dict()


class DriverBase(object):
    """
    Drivers
    -------

    """
    name = ''
    driver_type = ''
    _handler = None
    wants = ''

    def __init__(self, devices):
        """
        :param devices: Devices handled by the driver
        """
        self.devices = devices

        if self._handler:
            self.handler = self._handler()
        else:
            self.handler = None

    @classmethod
    def probe(cls, context_data):
        raise NotImplementedError

    def inspect(self):
        raise NotImplementedError


class PCIDriverBase(DriverBase):
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
        registered_drivers.append({
            'name': cls.name,
            'class': cls,
            'driver_type': cls.driver_type,
            'wants': cls.wants
        })

        return cls
    return decorator


def get_subsystem_drivers(subsystem):
    drivers = []
    for d in driver_class_cache:
        if driver_class_cache[d].driver_type == subsystem:
            drivers.append(driver_class_cache[d])
    return drivers


def set_driver_cache(d, devices):
    """
    Instantiate the driver and store it for later
    :param d: The driver to instantiate
    :param devices: return of the probe
    :return:
    """
    if not driver_class_cache.get(d['name']):
        log.info('Initializing d: %s' % d['name'])
        driver_class_cache[d['name']] = d['class'](devices)
