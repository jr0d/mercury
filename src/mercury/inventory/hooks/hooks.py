import logging

from mercury.inventory.hooks import interfaces


log = logging.getLogger(__name__)


HOOK_MAP = {
    'interfaces': interfaces.InterfaceHook,
    'lldp': interfaces.LLDPHook,
}


def run_hooks(hooks, data):
    """
    Calls the run method for each hook in the hooks dict.

    :param hooks: A dict of keys/hook classes
    :param data: Inventory data dict
    :return:
    """
    for hook_key, hook_class in hooks.items():
        hook = hook_class(data)
        log.info('Running {} hook'.format(hook_key))
        hook.run()


def get_hooks_from_data(data):
    """
    Returns a dict of hooks based on the keys present in the data dict

    :param data: Inventory data dict
    :return: dict
    """
    keys = set(data.keys()) & set(HOOK_MAP.keys())
    hooks = {key: HOOK_MAP[key] for key in keys}
    return hooks
