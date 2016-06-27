class AsyncInspector(object):
    def __init__(self, device_info, agent_configuration):
        self.device_info = device_info
        self.configuration = agent_configuration

    def inspect(self):
        """Cannot block"""
        raise NotImplemented

    def cleanup(self):
        """Called on agent exit"""
        raise NotImplemented