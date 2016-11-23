#
# Press plugin will add hooks for init, layout, download, and post. The hooks
# will update the mercury task with a progress delta and a custom action.
#
# The press 'complete' (or error) event will be handled by the native press
# orchestrator.

from press.hooks.hooks import add_hook

from mercury.agent.configuration import agent_configuration
from mercury.common.transport import SimpleRouterReqClient


def plugin_init(configuration):
    pass
