import logging

log = logging.getLogger(__name__)

registered_drivers = dict()
driver_pci_map = dict()


class PCIDriverBase(object):
    _handler = None

    def __init__(self, device_info):
        self.device_info = device_info

    @classmethod
    def probe(cls, pci_data):
        """
        Implementations should return a sorted list of PCI devices supported by the handler
        :param pci_data:
        :return:
        """
        raise NotImplementedError

    @property
    def handler(self):
        raise NotImplementedError


def driver(driver_type):
    def decorator(cls):
        log.info('Registering driver: %s' % cls.__name__)
        if driver_type in registered_drivers:
            registered_drivers[driver_type].append(cls)
        else:
            registered_drivers[driver_type] = [cls]
        return cls
    return decorator
