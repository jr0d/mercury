import time

import zmq

_messages = [
    'would you care for a spot of tea?',
    'i haven\'t got all day, what\'s it gonna be',
    'Ok',
    'I\'m throwing it out'
]

def pub():
    ctx = zmq.Context()
    socket = ctx.socket(zmq.PUB)
    socket.bind('tcp://*:9010')

    for message in _messages:
        print(f'Sending')
        socket.send(('requests %s' % message).encode('ascii'))
        time.sleep(20)

if __name__ == '__main__':
    pub()
