# Copyright 2018 Ruben Quinones (ruben.quinones@rackspace.com)
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

from flask import Flask

from mercury.boot.configuration import get_boot_configuration
from mercury.boot.urls import boot_urls

app = Flask(__name__)

# Add url rules
for url, view_func in boot_urls:
    app.add_url_rule(url, view_func=view_func, strict_slashes=False)

if __name__ == '__main__':
    configuration = get_boot_configuration()
    app.run(host=configuration.host, port=configuration.port, debug=True)
