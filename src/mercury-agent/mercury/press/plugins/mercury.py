#
# Press plugin will add hooks for init, layout, download, and post. The hooks
# will update the mercury task with a progress delta and a custom action.
#
# The press 'complete' (or error) event will be handled by the native press
# orchestrator.

import logging

from press.hooks.hooks import add_hook

from mercury.agent.client import BackEndClient

log = logging.getLogger(__name__)


def get_mercury_configuration(press_configuration):
    """
    Validates and returns our mercury configuration
    :param press_configuration: The full press configuration
    :return: (dict) mercury_configuration
    """
    required = ['task_id', 'backend_zurl']
    try:
        mercury_configuration = press_configuration['mercury']
    except KeyError:
        log.error('Mercury section is missing from press configuration')
        return

    missing = []
    for key in required:
        if key not in mercury_configuration:
            missing.append(key)

    if missing:
        log.error('Mercury configuration is missing: {}'.format(missing))
        return

    return mercury_configuration


# noinspection PyUnusedLocal
def super_hook(press_config, backend_client, task_id, action, progress):
    log.debug('Running Hook to update backend task: {} {}'.format(task_id, action))
    backend_client.task_update({
        'action': 'Press: ' + action,
        'task_id': task_id,
        'progress': progress
    })


def plugin_init(press_configuration):
    mc = get_mercury_configuration(press_configuration)
    if not mc:
        return

    backend_client = BackEndClient(mc['backend_zurl'])
    task_id = mc['task_id']
    add_hook(super_hook, 'post-press-init', backend_client, task_id, 'Starting', 0.0)
    add_hook(super_hook, 'pre-apply-layout', backend_client, task_id, 'Preparing Layout', 0.1)
    add_hook(super_hook, 'pre-image-acquire', backend_client, task_id, 'Downloading', 0.2)
    add_hook(super_hook, 'post-press-init', backend_client, task_id, '', 0.0)
    add_hook(super_hook, 'post-press-init', backend_client, task_id, '', 0.0)