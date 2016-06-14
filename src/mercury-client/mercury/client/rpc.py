import json
import requests


class InterfaceBase(object):
    SERVICE_URI = ''

    def __init__(self, target):
        self.target = target
        if self.SERVICE_URI:
            self.base_url = '{0}/{1}'.format(self.target, self.SERVICE_URI)
        else:
            self.base_url = self.target

        self.headers = {'Content-type': 'application/json'}

    def join_endpoint(self, endpoint):
        endpoint = endpoint.strip('/')
        if not endpoint:
            # endpoint is base_url
            return self.base_url
        return self.base_url + '/' + endpoint.lstrip('/')

    def append_header(self, extra_headers):
        if not extra_headers:
            return self.headers
        return extra_headers.update(self.headers)

    def get(self, endpoint='/', params=None, extra_headers=None):
        r = requests.get(self.join_endpoint(endpoint), params=params,
                         headers=self.append_header(extra_headers))
        r.raise_for_status()
        return r.json()

    def post(self, endpoint='/', data=None, params=None, extra_headers=None):
        r = requests.post(self.join_endpoint(endpoint), params=params, data=data,
                          headers=self.append_header(extra_headers))
        r.raise_for_status()
        return r.json()


class JobInterfaceBase(InterfaceBase):
    SERVICE_URI = 'api/rpc/jobs'


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
        r = self.post(data=json.dumps(_payload))

        self.job_id = r['job_id']

    def get_job(self):
        if not self.job_id:
            return

        return self.get(self.job_id)


class Jobs(JobInterfaceBase):
    def query(self):
        pass


if __name__ == '__main__':
    job_q = JobQuery('http://mercury:9005', {'raid.0.slot': '3'},
                     {'method': 'hpssa_create_array', 'kwargs': {
        'slot': 3,
        'selection': '1I:1:1,1I:1:2,1I:1:3,1I:1:4,1I:1:5,1I:1:6,1I:1:7,1I:1:8',
        'raid': '1+0'
    }})
    job_q.post_job()
    from pprint import pprint
    pprint(job_q.get_job())
    pprint(job_q.job_id)
    import time
    time.sleep(10)
    pprint(job_q.get_job())

    jobs = Jobs('http://mercury:9005')
    pprint(jobs.get())

