import logging
import threading



log = logging.getLogger(__name__)


class ActiveInventoryRuntimeHandler(object):
    def __init__(self, active_collection):
        """

        :param active_collection:
        """
        log.info('Using collection {}'.format(active_collection.name))
        self.active_collection = active_collection

        cursor = self.active_collection.find()
        # Load (reacquire)

    def
