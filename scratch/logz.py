import logging


class DemoHandler(logging.Handler):
    def emit(self, record):
        print(record)
        print(vars(record))
        if hasattr(record, 'press_event'):
            print(record.press_event)


log = logging.getLogger('NONYA')
log.setLevel(logging.DEBUG)
log.addHandler(DemoHandler())

log.info('EAD')
log.info('EAD', extra={'press_event': 'EAD'})

