import asyncio
import logging

import msgpack
import zmq
import zmq.asyncio

from mercury.common.transport import parse_multipart_message
from mercury.common.exceptions import parse_exception, fancy_traceback_short, MercuryClientException

import motor
import motor.motor_asyncio


# ctx = zmq.asyncio.Context()
# loop = zmq.asyncio.ZMQEventLoop()
# asyncio.set_event_loop(loop)

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class TestAsync(object):
    def __init__(self, bind_address='tcp://*:9000', loop=None):
        self.bind_address = bind_address
        self.loop = loop
        self.context = zmq.asyncio.Context()
        self.socket = self.context.socket(zmq.ROUTER)

        log.debug('Bound to: ' + self.bind_address)

        self.socket.bind(self.bind_address)

    async def receive(self):
        multipart = await self.socket.recv_multipart()
        parsed_message = parse_multipart_message(multipart)

        try:
            message = msgpack.unpackb(parsed_message['message'], encoding='utf-8')
        except TypeError as type_error:
            await self.send_error(parsed_message['address'],
                                  'Received unpacked, non-string type: %s : %s' % (type(parsed_message),
                                                                                   type_error))
            raise MercuryClientException('Message is malformed')
        except (msgpack.UnpackException, msgpack.ExtraData) as msgpack_exception:
            await self.send_error(parsed_message['address'], 'Received invalid request: %s' % str(
                msgpack_exception)), None
            raise MercuryClientException('Message is malformed')
        return parsed_message['address'], message

    async def send_error(self, address, message):
        data = {'error': True, 'message': message}
        log.error(message)
        await self.send(address, data)

    async def send(self, address, message):
        await self.socket.send_multipart(address + [msgpack.packb(message)])

    # noinspection PyMethodMayBeStatic
    async def process(self, message):
        mc = motor.motor_asyncio.AsyncIOMotorClient()
        db = mc['test']
        collection = db['your_mom']

        await collection.insert_one({'apple': 'pen'})

        log.info('Message: {!r}'.format(message))
        return {'status': 'AOK'}

    async def start(self):
        while True:
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


if __name__ == '__main__':
    loop = zmq.asyncio.ZMQEventLoop()
    asyncio.set_event_loop(loop)
    test_async = TestAsync()
    try:
        loop.run_until_complete(test_async.start())
    except KeyboardInterrupt:
        pass
    finally:
        test_async.socket.close(0)
        test_async.context.destroy()
        loop.close()
