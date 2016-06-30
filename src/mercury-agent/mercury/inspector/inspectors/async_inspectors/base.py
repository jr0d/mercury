import threading


class AsyncInspector(object):
    def __init__(self, t):
        self.t = t
        self.kill = False

    def start(self, target, *args, **kwargs):
        self.t = threading.Thread(target=target, args=args, kwargs=kwargs)
        self.t.start()

    def inspect(self):
        raise NotImplementedError
