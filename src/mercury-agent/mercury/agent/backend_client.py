from mercury.agent.configuration import agent_configuration
from mercury.common.clients.rpc.backend import BackEndClient


# Private
__backend_client = None


def get_backend_client():
    # TODO: Trying this out, 0mq says it is ok
    global __backend_client
    if not __backend_client:
        __backend_client = BackEndClient(agent_configuration['remote']['rpc_service'])
    return __backend_client
