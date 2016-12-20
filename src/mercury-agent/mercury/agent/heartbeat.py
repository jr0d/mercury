"""
Why isn't this used...


Because, in this instance, where the server acts as an RPC dispatcher
to agents that may or may not be alive, it makes sense to implement a ping
pong from the server.
"""

# import logging
# import multiprocessing
# import os
# import time
#
# from mercury.common.transport import SimpleRouterReqClient
#
# log = logging.getLogger(__name__)
#
#
# def heartbeat(client, mercury_id):
#     try:
#         loadavg = os.getloadavg()
#     except OSError as os_error:
#         # Issue: https://github.com/jr0d/mercury/issues/4
#         log.error('Error getting load average: %s' % str(os_error))
#         loadavg = (0.0, 0.0, 0.0)
#
#     message = {
#         'message_type': 'heartbeat',
#         'payload': {
#             'load_average': loadavg,
#             'timestamp': time.time(),
#             'mercury_id': mercury_id
#         }
#     }
#     try:
#         response = client.transiever(message)
#     except:
#         pass
#
# def heartbeat_start(mercury_id, zmq_url, interval=15):
#     log.info('Starting heartbeat service - {} - interval {}'.format(zmq_url, interval))
#     client = SimpleRouterReqClient(zmq_url, linger=0, response_timeout=5)
