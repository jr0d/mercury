from mercury.inventory.hooks import base


class InterfaceHook(base.Hook):
    """
    Interface data handler, this should run when updating interface data for
    a given inventory record.
    """

    def process_data(self):
        """
        Convert interface data to mongodb dot notation in order to update the
        inventory record without erasing data collected asynchronously.
        """
        interfaces = self.data.pop('interfaces', [])
        for i, interface in enumerate(interfaces):
            for key, value in interface.items():
                new_key = 'interfaces.{}.{}'.format(i, key)
                self.data[new_key] = value

    def run(self):
        self.process_data()


class LLDPHook(base.Hook):
    """
    Interface LLDP data handler, this should run when updating LLDP data for
    a given inventory interface.
    """

    def process_data(self):
        """
        Convert interface LLDP data to mongodb dot notation in order to update
        the interface specified by the 'interface_index' key.
        """
        try:
            lldp = self.data.pop('lldp')
            interface_index = lldp.pop('interface_index')
        except KeyError:
            raise base.HookException('Missing LLDP data')
        lldp_key = 'interfaces.{}.lldp'.format(interface_index)
        self.data[lldp_key] = lldp

    def run(self):
        self.process_data()
