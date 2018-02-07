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

import os
import logging

from flask import request, send_file, abort, jsonify
from flask.views import MethodView

from werkzeug.utils import secure_filename

from mercury.common.clients.inventory import InventoryClient
from mercury.boot.configuration import get_boot_configuration


log = logging.getLogger(__name__)
configuration = get_boot_configuration()


class BootView(MethodView):
    """
    Boot method view
    """

    def __init__(self, *args, **kwargs):
        super(BootView, self).__init__(*args, **kwargs)
        inventory_url = configuration.inventory.inventory_router
        self.inventory_client = InventoryClient(inventory_url)

    def get(self, mac_address=None):
        """
        Main boot endpoint 

        :param mac_address: Inventory object mac_address, default is None.
        :return: Boot file.
        """
        if mac_address:
            result = self.inventory_client.query(
                {
                    'interfaces.address': mac_address
                }
            )

            try:
                inventory = result['message']['items'][0]
            except IndexError:
                return abort(404)
                
            # Select boot file depending on inventory attributes
            # if inventory and inventory.dmi.platform == 'Dell, Inc.':
            #     return send_file(some_custom_dell_boot_menu)

        return send_file(configuration.default_boot_file)



class FileView(MethodView):
    """ 
    File method view 
    """

    def get(self, path=''):
        abs_path = os.path.join(configuration.file_upload_directory, path)

        if not os.path.exists(abs_path):
            return abort(404)

        if os.path.isfile(abs_path):
            return send_file(abs_path)

        files = os.listdir(abs_path)

        response = []

        for file_name in files:
            file_path = os.path.join(configuration.file_upload_directory,
                                     file_name)
            data = self._get_file_data(file_name, file_path)
            response.append(data)

        return jsonify(response)

    def post(self):
        """
        Upload a file to the upload directory
        :return: None
        """
        upload = request.files['file']

        if upload and upload.filename:
            file_name = secure_filename(upload.filename)
            file_path = os.path.join(configuration.file_upload_directory,
                                     file_name)
            upload.save(file_path)
            data = self._get_file_data(file_name, file_path)

            return jsonify(data)

        return abort(400)

    def delete(self, path):
        """
        Delete the file defined by path relative to the upload directory
        :param path: File path
        :return: None
        """
        abs_path = os.path.join(configuration.file_upload_directory, path)

        if not os.path.exists(abs_path):
            return abort(404)

        if os.path.isfile(abs_path):
            os.remove(abs_path)
        else:
            os.removedirs(abs_path)

        return '', 204

    def _get_file_data(self, file_name, file_path):
        file_mtime = os.path.getmtime(file_path)
        file_size = os.path.getsize(file_path)
        file_link = 'http://{}:{}/file/{}'.format(configuration.host,
                                                  configuration.port,
                                                  file_name)
        file_type = 'file'

        if os.path.isdir(file_path):
            file_type = 'directory'

        data = {
            'name': file_name,
            'type': file_type,
            'link': file_link,
            'mtime': file_mtime,
            'size': file_size,
        }

        return data