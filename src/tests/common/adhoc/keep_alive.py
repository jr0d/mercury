from mercury.common.clients.router_req_client import RouterReqClient

c = RouterReqClient('tcp://localhost:9090')

print(c.transceiver({'_protocol_message': 'keep_alive'}))

input('=>')
