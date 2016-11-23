# from mercury.agent.
from size import PercentString, Size


WRITE_POLICY = {
    'DEFAULT': 0,
    'WRITE_BACK': 1,
    'WRITE_THROUGH': 2
}


class RAIDSizeException(Exception):
    pass


class RAIDIndexException(Exception):
    pass


class RAIDActions(object):
    def get_configuration(self, adapter):
        raise NotImplementedError

    def get_physical_disks(self, adapter):
        raise NotImplementedError

    def get_logical_drive(self, adapter):
        raise NotImplementedError

    def create_logical_drive(self, adapter, level, disks, size=None, array=None, hot_spares=None, caching=True,
                             write_policy=WRITE_POLICY['WRITE_BACK'], quick_initialization=True):
        """

        :param adapter:
        :param level:
        :param disks:
        :param size:
        :param array:
        :param hot_spares:
        :param caching:
        :param write_policy:
        :param quick_initialization:
        :return:
        """
        raise NotImplementedError

    def delete_logical_drive(self, adapter, ld):
        raise NotImplementedError

    def clear_configuration(self, adapter):
        raise NotImplementedError

    def calculate_size(self, adapter, disks, size, array=None):
        """
        A helper intended to calculate and check bounds of percent, string, and byte represented sizes
        :param adapter:
        :param disks:
        :param size:
        :param array:
        :return:
        """
        # Solving this from the ground up, this will most likely move higher up
        configuration = self.get_configuration(adapter)

        if not configuration:
            raise RAIDIndexException('The target adapter does not seem to exist')

        # This too, as we need these things before we calculate size
        try:
            target_array = configuration.get('arrays', [])[array]
        except IndexError:
            raise RAIDIndexException('Array index {} does not exist on Adapter {}'.format(array, adapter))

        # This should move to a helper function, is_percent_string?
        if isinstance(size, str):
            if '%' in size:
                return size

        size = Size(size)

        if array:
            array_free_space = Size(target_array['free_space'])
            if Size(array_free_space) < size:
                raise RAIDSizeException('{} exceeds free space on the array, {}'.format(size, array_free_space))

