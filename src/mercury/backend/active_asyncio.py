import asyncio
import logging
import time

import msgpack
import zmq
import zmq.asyncio

from mercury.common.asyncio.clients.inventory import InventoryClient

log = logging.getLogger(__name__)

active_state = {}
stop_ping_loop = False


def stop_ping():
    global stop_ping_loop
    stop_ping_loop = True


def add_active_record(record):
    log.info('Adding record, {mercury_id}, to active state'.format(**record))
    active_state.update({
        record['mercury_id']: {
            'mercury_id': record['mercury_id'],
            'rpc_address': record['active']['rpc_address'],
            'rpc_address6': record['active']['rpc_address6'],
            'ping_port': record['active']['ping_port'],
            'last_ping': 0,
            'pinging': False
        }
    })


async def ping(record, ctx, timeout, retries, backoff, inventory_client):
    """
    ping node until it responds or encounters x timeouts of x*backoff
    :param timeout:
    :param backoff:
    :param retries:
    :param record:
    :param ctx:
    :param inventory_client:
    :return:
    """
    failures = 0

    zurl = 'tcp://{}:{}'.format(record['rpc_address6'] or record['rpc_address'],
                                record['ping_port'])

    while failures < retries:
        socket = ctx.socket(zmq.REQ)
        socket.setsockopt(zmq.LINGER, 0)
        socket.connect(zurl)
        log.debug(socket)
        payload = {
            'message': 'ping',
            'timestamp': time.time()
        }
        current_timeout = int((timeout + (failures and timeout or 0) * (failures**backoff)))
        log.debug('Pinging %s , payload: %s, timeout: %d' % (zurl, payload, current_timeout))

        await socket.send(msgpack.packb(payload))

        if await socket.poll(current_timeout):  # Success condition
            reply = await socket.recv()  # Data is ready for snarfing

            log.debug("ping success: %s : %s" % (
                zurl, msgpack.unpackb(reply, encoding='utf-8')))
            socket.close()

            active_state[record['mercury_id']]['last_ping'] = time.time()
            active_state[record['mercury_id']]['pinging'] = False
            return

        log.debug('ping timeout failures/backoff: {}/{}  : {} : {}'.format(
            failures, backoff, record['mercury_id'], zurl))

        failures += 1

        socket.close()

    log.info('{} timed out, removing active record'.format(record['mercury_id']))

    # remove agent data from the database
    # this will await until the inventory is available
    await inventory_client.update_one(
        record['mercury_id'], {'active': None})

    # remove the record from the state data structure
    del active_state[record['mercury_id']]


async def ping_loop(ctx,
                    ping_interval,
                    cycle_time,
                    initial_ping_timeout,
                    ping_retries,
                    backoff,
                    loop,
                    inventory_router_url):
    """

    :param ctx:
    :param ping_interval:
    :param cycle_time:
    :param initial_ping_timeout:
    :param ping_retries:
    :param backoff:
    :param loop:
    :param inventory_router_url:
    :return:
    """
    # load the queue
    inventory_client = InventoryClient(inventory_router_url, linger=0)
    inventory_client.service_name = 'Inventory Service'

    while True:
        if stop_ping_loop:
            log.info('Stopping ping loop')
            break
        now = time.time()
        for mercury_id, data in list(active_state.items()):  # copy to list because the list length could change
            # out from under us
            if now - data['last_ping'] > ping_interval and not data['pinging']:
                log.debug('Scheduling ping for {}'.format(mercury_id))
                active_state[mercury_id]['pinging'] = True
                asyncio.ensure_future(ping(data, ctx, initial_ping_timeout, ping_retries, backoff, inventory_client),
                                      loop=loop)
        await asyncio.sleep(cycle_time)
