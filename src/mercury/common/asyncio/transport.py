import logging

import msgpack
import zmq
import zmq.asyncio

from mercury.common.exceptions import fancy_traceback_short, MercuryClientException, parse_exception
from mercury.common.transport import parse_multipart_message

log = logging.getLogger(__name__)


class AsyncRouterReqService(object):
    def __init__(self, bind_address, linger=-1, poll_timeout=2, loop=None):
        self.bind_address = bind_address
        self.loop = loop
        self.context = zmq.asyncio.Context()
        self.poll_timeout = poll_timeout
        self.socket = self.context.socket(zmq.ROUTER)
        self.socket.setsockopt(zmq.LINGER, linger)

        self.in_poller = zmq.asyncio.Poller()
        self.in_poller.register(self.socket, zmq.POLLIN)

        log.info('Bound to: ' + self.bind_address)

        self.socket.bind(self.bind_address)

        self._kill = False

    async def receive(self):
        multipart = await self.socket.recv_multipart()
        parsed_message = parse_multipart_message(multipart)

        if not parsed_message:
            log.error('Received junk off the wire')
            raise MercuryClientException('Message is malformed')

        try:
            message = msgpack.unpackb(parsed_message['message'], encoding='utf-8')
        except TypeError as type_error:
            log.error('Received unpacked, non-string type: %s : %s' % (type(parsed_message),
                                                                       type_error))
            await self.send_error(parsed_message['address'], 'Client error, message is not packed')
            raise MercuryClientException('Message is malformed')

        except (msgpack.UnpackException, msgpack.ExtraData) as msgpack_exception:
            log.error('Received invalid request: %s' % str(
                msgpack_exception))

            await self.send_error(parsed_message['address'], 'Client error, message is malformed')
            raise MercuryClientException('Message is malformed')

        return parsed_message['address'], message

    async def send_error(self, address, message):
        data = {'error': True, 'message': message}
        log.error(message)
        await self.send(address, data)

    async def send(self, address, message):
        await self.socket.send_multipart(address + [msgpack.packb(message)])

    async def process(self, message):
        raise NotImplementedError

    async def start(self):
        while not self._kill:
            if not await self.in_poller.poll(self.poll_timeout * 1000):
                log.debug('Receive Poll Timeout')
                continue
            try:
                address, msg = await self.receive()
            except MercuryClientException:
                continue
            # noinspection PyBroadException
            try:
                response = await self.process(msg)
            except MercuryClientException as mce:
                await self.send_error(address, 'Encountered client error: {}'.format(mce))
                continue

            except Exception:
                exec_dict = parse_exception()
                log.error('process raised an exception and should not have.')
                log.error(fancy_traceback_short(exec_dict))
                await self.send_error(address, 'Encountered server error, sorry')
                continue
            await self.send(address, response)

        log.info('Goodbye Cruel World')
        self.cleanup()

    def kill(self):
        self._kill = True

    @staticmethod
    def get_key(key, data):
        try:
            return data[key]
        except KeyError:
            raise MercuryClientException('{} is missing from request'.format(key))

    @staticmethod
    def validate_required(required, data):
        missing = []
        for key in required:
            if key not in data:
                missing.append(data)

        if missing:
            raise MercuryClientException('Message is missing required data: {}'.format(missing))

    def cleanup(self):
        self.socket.close(0)
        self.context.destroy()
