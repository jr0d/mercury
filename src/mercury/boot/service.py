# Copyright 2017 Ruben Quinones (ruben.quinones@rackspace.com)
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import logging

from gevent.wsgi import WSGIServer

from mercury.boot.configuration import get_boot_configuration
from mercury.boot.app import app

log = logging.getLogger(__name__)


def main():
    """
    Gevent WSGI server launcher with graceful stop.
    """
    config = get_boot_configuration()
    logging.basicConfig(
        level=logging.getLevelName(config.logging.level),
        format=config.logging.format)
    http_server = WSGIServer((config.host, config.port), app)

    try:
        log.info('Starting gevent WSGI service')
        http_server.serve_forever()
    except KeyboardInterrupt:
        log.info('Stopping gevent WSGI service')
        http_server.stop()


if __name__ == '__main__':
    main()
