
# Target
from mercury.common.helpers import cli


def test_find_in_path():
    present_relative = 'ls'
    missing_relative = 'xxxxxxx'

    present_absolute = '/usr/bin/ls'
    missing_absolute = '/usr/bin/xxxxxxx'

    assert cli.find_in_path(present_relative) is not None
    assert cli.find_in_path(missing_relative) is None
    assert cli.find_in_path(present_absolute) is not None
    assert cli.find_in_path(missing_absolute) is None


def test_attribute_string():
    print(cli.CLIResult(b'HELLO'))
    print(cli.run('ls'))


if __name__ == '__main__':
    test_attribute_string()
