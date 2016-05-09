from mercury.hardware import platform_detection
from mercury.hardware.drivers import driver, PCIDriverBase
from mercury.hardware.raid.interfaces.hpsa.hpssa import HPSSA


@driver(driver_type='raid')
class SmartArrayDriver(PCIDriverBase):
    _handler = HPSSA
    PCI_DEVICE_IDS = [platform_detection.SMART_ARRAY_DEVICE_ID_9]

    @classmethod
    def probe(cls, pci_data):
        raid_pci_devices = platform_detection.get_raid_controllers(cls.device_info['pci'])
        if not platform_detection.has_smart_array_gen9(pci_data=raid_pci_devices):
            return

        owns = list()
        for device in raid_pci_devices:
            if device['device_id'] in cls.PCI_DEVICE_IDS:
                owns.append(device['slot'])
        return owns

    @property
    def handler(self):
        return self._handler()
