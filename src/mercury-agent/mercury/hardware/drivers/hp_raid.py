from mercury.hardware import platform_detection
from mercury.hardware.drivers import driver, DriverBase
from mercury.hardware.raid.interfaces.hpsa.hpssa import HPSSA


@driver()
class SmartArrayDriver(DriverBase):
    _handler = HPSSA

    def probe(self):
        return platform_detection.has_smart_array_gen9(self.device_info.get('pci'))

    @property
    def handler(self):
        return self._handler()
