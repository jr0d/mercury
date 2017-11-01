import unittest

from mock import patch

from mercury.inventory import hooks


class MercuryInventoryHookTests(unittest.TestCase):
    """
    General hook unit tests.
    """

    def test_get_hooks_from_data(self):
        data = {'lldp': None, 'random': 1234}
        hook_dict = hooks.get_hooks_from_data(data)
        self.assertDictEqual(hook_dict, {'lldp': hooks.LLDPHook})

    @patch('mercury.inventory.hooks.LLDPHook.run')
    def test_run_hooks(self, lldp_run):
        lldp_run.return_value = None
        data = {'lldp': None, 'random': 1234}
        hook_dict = hooks.get_hooks_from_data(data)
        hooks.run_hooks(hook_dict, data)
        lldp_run.assert_called_once()


class MercuryInventoryLLDPHookTests(unittest.TestCase):
    """
    LLDP hook unit tests.
    """

    def test_lldp_hook(self):
        data = {
            'lldp': {
                'switch_name': 'someswitch',
                'switch_port': 'someport',
                'interface_index': 0,
            }
        }

        lldp_hook = hooks.LLDPHook(data)
        lldp_hook.run()

        expected_data = {
            'interfaces.0.lldp': {
                'switch_name': 'someswitch',
                'switch_port': 'someport',
            }
        }

        self.assertDictEqual(data, expected_data)

    def test_lldp_hook_exception(self):
        data = {
            'lldp': {
                'switch_name': 'someswitch',
                'switch_port': 'someport',
            }
        }

        lldp_hook = hooks.LLDPHook(data)

        self.assertRaises(hooks.HookException, lldp_hook.run)


class MercuryInventoryInterfaceHookTests(unittest.TestCase):
    """
    Interface hook unit tests.
    """

    def test_interface_hook(self):
        data = {
            'interfaces': [
                {
                    'name': 'eno1',
                    'subdict': {'subkey': None},
                }
            ]
        }

        interface_hook = hooks.InterfaceHook(data)
        interface_hook.run()

        expected_data = {
            'interfaces.0.name': 'eno1',
            'interfaces.0.subdict': {'subkey': None},
        }

        self.assertDictEqual(data, expected_data)

    def test_interface_hook_is_empty(self):
        data = {}
        interface_hook = hooks.InterfaceHook(data)
        interface_hook.run()
        self.assertEqual(data, {})
