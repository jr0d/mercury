import signal
import asyncio


def make_sleep():
    async def sleep(delay, result=None, *, loop=None):
        coro = asyncio.sleep(delay, result=result, loop=loop)
        task = asyncio.ensure_future(coro)
        sleep.tasks.add(task)
        try:
            return await task
        except asyncio.CancelledError:
            return result
        finally:
            sleep.tasks.remove(task)

    sleep.tasks = set()
    sleep.cancel_all = lambda: sum(task.cancel() for task in sleep.tasks)
    return sleep


s = make_sleep()


# noinspection PyUnusedLocal
def term_handler(*args, **kwargs):
    print('Shutting Down!')


async def compute(x, y):
    print("Compute %s + %s ..." % (x, y))
    await asyncio.sleep(4.0)
    return x + y

async def print_sum(x, y):
    result = await compute(x, y)
    print("%s + %s = %s" % (x, y, result))


loop = asyncio.get_event_loop()
signal.signal(signal.SIGTERM, term_handler)

f = asyncio.ensure_future(print_sum(10, 25))

try:
    loop.run_until_complete(print_sum(1, 2))
except KeyboardInterrupt:
    print('Keyboard Interrupt')
    term_handler()  # This is where we should send the kill
finally:
    pending = asyncio.Task.all_tasks()
    loop.run_until_complete(asyncio.gather(*pending))  # here all sleeps/tasks will finish..
    # and we'll cleanly shut down!
