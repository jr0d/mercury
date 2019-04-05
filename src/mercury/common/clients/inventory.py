# Copyright 2015 Jared Rodriguez (jared.rodriguez@rackspace.com)
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

from mercury.common.exceptions import MercuryClientException
from mercury.common.clients.router_req_client import RouterReqClient


class InventoryClient(RouterReqClient):
    """Client to interact with inventory."""

    service_name = 'Inventory'

    def insert_one(self, device_info):
        """Insert a new device in inventory.

        :param device_info: A dict containing the new device info.
        :returns: The 'response' field of the transceiver's reply.
        :raises: MercuryClientException if 'mercury_id' is missing.
        """
        mercury_id = device_info.get('mercury_id')
        if not mercury_id:
            raise MercuryClientException('device_info is missing mercury_id')

        payload = {
            'endpoint': 'insert_one',
            'args': [device_info]
        }
        return self.transceiver(payload)

    def update_one(self, mercury_id, update_data):
        """Update a device in inventory.

        :param mercury_id: The ID of the device to update.
        :param update_data: A dict containing the data to update.
        :returns: The 'response' field of the transceiver's reply.
        """
        payload = {
            'endpoint': 'update_one',
            'args': [mercury_id],
            'kwargs': {'update_data': update_data}
        }

        return self.transceiver(payload)

    def get_one(self, mercury_id, projection=None):
        """Get a device from inventory.

        :param mercury_id: The ID of the device.
        :param projection: A dict specifying which fields should be included
            in the results.
        :returns: The 'response' field of the transceiver's reply.
        """
        payload = {
            'endpoint': 'get_one',
            'args': [mercury_id],
            'kwargs': {
                'projection': projection
            }
        }
        return self.transceiver(payload)

    def query(self, query_data, projection=None, limit=0, sort='_id',
              sort_direction=1, offset_id=None):
        """Query inventory for devices matching query_data.

        :param query_data: A dict to filter the results.
        :param projection: A dict specifying which fields should be included
            in the results.
        :param limit: The maximum number of results to return.
        :param sort: The sort key default `_id`
        :param sort_direction: The sort direction.
        :param offset_id: The offset_id to use for paging
        :returns: The 'response' field of the transceiver's reply.
        """
        payload = {
            'endpoint': 'query',
            'args': [query_data],
            'kwargs': {
                'projection': projection,
                'limit': limit,
                'sort': sort,
                'sort_direction': sort_direction,
                'offset_id': offset_id
            }
        }
        return self.transceiver(payload)

    def delete(self, mercury_id):
        """Delete a device from inventory.

        :param mercury_id: The ID of the device.
        :returns: The 'response' field of the transceiver's reply.
        """
        payload = {
            'endpoint': 'delete',
            'args': [mercury_id]
        }
        return self.transceiver(payload)

    def count(self, query_data):
        """Count how many devices match query_data.

        :param query_data: A dict to filter the results.
        :returns: The 'response' field of the transceiver's reply.
        """
        payload = {
            'endpoint': 'count',
            'args': [query_data]
        }
        return self.transceiver(payload)

    def update_boot(self, mercury_id, update_data):
        """

        :param mercury_id:
        :param update_data:
        :return:
        """
        payload = {
            'endpoint': 'update_boot',
            'args': [mercury_id, update_data]
        }
        return self.transceiver(payload)

    def update_boot_many(self, query, update_data):
        """

        :param query:
        :param update_data:
        :return:
        """
        payload = {
            'endpoint': 'update_boot_many',
            'args': [query, update_data]
        }
        return self.transceiver(payload)
