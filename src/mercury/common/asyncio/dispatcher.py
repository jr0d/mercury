import logging
import sys
import traceback

from mercury.common.exceptions import EndpointError

log = logging.getLogger(__name__)


class AsyncDispatcher(object):
    def __init__(self, controller, acknowledge_only=False):
        """
        Asynchronous generic dispatcher

        :param controller: An controller containing async endpoints
        :param acknowledge_only: Immediately sync the response to the client
        request.
        """
        self.controller = controller
        log.debug(f'Registered endpoints: {self.controller.endpoints}')

    async def dispatch(self, message):
        endpoint = message.get('endpoint')
        args = message.get('args', [])
        kwargs = message.get('kwargs', {})

        if not endpoint:
            log.debug('Received message with no endpoint')
            return dict(error=True, message='Endpoint not specified in message')

        if endpoint not in self.controller.endpoints:
            log.debug('Received request to unsupported endpoint: %s' % endpoint)
            return dict(error=True, message='Endpoint is not supported')

        # noinspection PyBroadException
        try:
            response = await self.controller.endpoints[endpoint](
                self.controller, *args, **kwargs)
        except EndpointError as endpoint_error:
            tb = traceback.format_exception(*sys.exc_info())
            log.error('Endpoint Error: endpoint=%s, message=%s, traceback=%s' % (
                endpoint,
                endpoint_error.message,
                '\n'.join(tb)
            ))
            return dict(error=True, traceback=tb, message=endpoint_error.message)
        except Exception as e:
            tb = traceback.format_exception(*sys.exc_info())
            log.error('An unhandled exception has been encountered: endpoint=%s,'
                      ' message=%s, traceback=%s' % (
                endpoint,
                str(e),
                '\n'.join(tb)
            ))
            return dict(error=True, traceback=tb, message=str(e))

        return dict(error=False, message=response)
