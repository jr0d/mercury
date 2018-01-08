import logging

from mercury.common.transport import SimpleRouterReqService


log = logging.getLogger('__name__')


class FakeAgentService(SimpleRouterReqService):
    def process(self, message):
        log.info(f'Received message: {message}')
        return {'message': dict(status=0, data=message)}


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    service = FakeAgentService('tcp://0.0.0.0:9090')
    service.start()
