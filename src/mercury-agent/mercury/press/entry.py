import logging

from mercury.agent.configuration import agent_configuration
from mercury.agent.client import BackEndClient

from press.main import Press
from press.plugin_init import init_plugins


log = logging.getLogger('mercury.press.main')


def entry(press_configuration):
    log.info('Initializing plugins')

    plugin_dirs = agent_configuration.get('press', {}).get('plugin_dirs')
    init_plugins(press_configuration, plugin_dirs)

    backend_url = agent_configuration['remote']['rpc_service']

    backend = BackEndClient
    try:
        press = Press(press_configuration)
    except Exception:
        log.error('Error during initialization')
        raise
    try:
        press.run()
    except Exception:
        log.error('Error during deployment')
        raise
    finally:
        if press.layout.committed:
            press.teardown()
