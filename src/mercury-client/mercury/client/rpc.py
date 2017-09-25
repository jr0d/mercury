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

from mercury.client.base import InterfaceBase


class JobInterfaceBase(InterfaceBase):
    SERVICE_URI = 'api/rpc/jobs'


class TaskInterface(InterfaceBase):
    SERVICE_URI = 'api/rpc/tasks'


class JobQuery(JobInterfaceBase):
    def __init__(self, target, query, instruction):
        super(JobQuery, self).__init__(target)
        self.query = query
        self.instruction = instruction

        self.job_id = None
        self.response_data = None

    def post_job(self):
        _payload = {
            'query': self.query,
            'instruction': self.instruction
        }
        r = self.post(data=_payload)
        try:
            self.job_id = r['job_id']
        except KeyError:
            raise Exception('Missing job_id, data contains: {}'.format(r))

    def status(self):
        return self.get('{}/status'.format(self.job_id))

    def tasks(self):
        return self.get('{}/tasks'.format(self.job_id))


class ActiveComputers(InterfaceBase):
    SERVICE_URI = 'api/active/computers'


#
# if __name__ == '__main__':
#     # job_q = JobQuery('http://mercury:9005', {'raid.0.slot': '3'},
#     #                  {'method': 'hpssa_create_array', 'kwargs': {
#     #     'slot': 3,
#     #     'selection': '1I:1:1,1I:1:2,1I:1:3,1I:1:4,1I:1:5,1I:1:6,1I:1:7,1I:1:8',
#     #     'raid': '1+0'
#     # }})
#     # job_q.post_job()
#     from pprint import pprint
#     # pprint(job_q.get_job())
#     # pprint(job_q.job_id)
#     # import time
#     # time.sleep(10)
#     # pprint(job_q.get_job())
#     #
#     # jobs = Jobs('http://mercury:9005')
#     # pprint(jobs.get())
#     ac = ActiveComputers('http://mercury:9005')
#     # pprint(ac.get())
#     pprint(ac.get(params={'projection': 'mercury_id'}))
#
#     url = "http://mercury:9005"
#     m_id = '017f3b1adc67a79050e3655747a0b6b0711c81ad68'
#
#     def clear_config(slot):
#         job_q = JobQuery(
#             url,
#             {
#                 'mercury_id': m_id
#             },
#             {
#                 'method': 'hpssa_clear_configuration',
#                 'kwargs': {
#                     'slot': slot
#                 }
#             }
#         )
#
#         job_q.post_job()
#         pprint(job_q.job_id)
#
#     def create_array(slot):
#         job_q = JobQuery(
#             url,
#             {
#                 'mercury_id': m_id
#             },
#             {
#                 'method': 'hpssa_create_array',
#                 'kwargs': {
#                     'slot': slot,
#                     'selection': '1I:1:1,1I:1:2',
#                     'raid': '0'
#                 }
#             }
#         )
#
#         job_q.post_job()
#         pprint(job_q.job_id)
#     # import time
#     # time.sleep(10)
#
#     # create_array(0)
#     clear_config(0)
