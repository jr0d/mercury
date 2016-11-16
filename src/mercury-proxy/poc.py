"""

Basically, we will build a service that ushers communication between isolated networks
This service will be of the router / dealer construction if possible.

Consider the registration process. An agent connects to the registration service and publishes
it's ip address. This direction is easy:

ROUTER tcp://1.1.1.2:9000 <=> (REQ) PROXY tcp://1.1.1.1:9000 (REP)<=> (REQ) (Agent)

But, since the agent is on an isolated network, how does one send messages directly to the
agent through the zmq proxy service. My hunch is that this behavior is not the intent of the proxy
service at all, but I could be mistaken. Since addresses are abstracted away, how might I properly
route to the correct agent.


RPC PUB

"""


import zmq

ctx = zmq.Context()

frontend = ctx.socket(zmq.ROUTER)
backend = ctx.socket(zmq.DEALER)

frontend.bind('tcp://*:9006')
backend.connect('tcp://localhost:9000')

zmq.proxy(frontend, backend)

