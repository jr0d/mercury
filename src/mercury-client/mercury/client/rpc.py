import json
import requests


def check_error(f):
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except requests.exceptions.HTTPError as http_error:
            try:
                data = http_error.response.json()
            except ValueError:
                data = http_error.response.text
            return {'error': True, 'code': http_error.response.status_code, 'data': data}
    return wrapper


class InterfaceBase(object):
    SERVICE_URI = ''

    def __init__(self, target, max_items=100):
        self.target = target
        if self.SERVICE_URI:
            self.base_url = '{0}/{1}'.format(self.target, self.SERVICE_URI)
        else:
            self.base_url = self.target

        self.headers = {'Content-type': 'application/json'}

        self.max_items = max_items

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

    @check_error
    def get(self, item='', params=None, extra_headers=None):
        r = requests.get(self.join_endpoint(item), params=params,
                         headers=self.append_header(extra_headers))
        r.raise_for_status()
        return r.json()

    @check_error
    def post(self, item='', data=None, params=None, extra_headers=None):
        r = requests.post(self.join_endpoint(item), params=params, data=json.dumps(data),
                          headers=self.append_header(extra_headers))
        r.raise_for_status()
        return r.json()

    @check_error
    def query(self, query, item='/query', projection=None, params=None, extra_headers=None):
        params = params or {}
        if projection:
            params['projection'] = ','.join(projection)

        return self.post(item, data={'query': query}, params=params, extra_headers=extra_headers)


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


class ActiveComputers(InterfaceBase):
    SERVICE_URI = 'api/active/computers'


if __name__ == '__main__':
    # job_q = JobQuery('http://mercury:9005', {'raid.0.slot': '3'},
    #                  {'method': 'hpssa_create_array', 'kwargs': {
    #     'slot': 3,
    #     'selection': '1I:1:1,1I:1:2,1I:1:3,1I:1:4,1I:1:5,1I:1:6,1I:1:7,1I:1:8',
    #     'raid': '1+0'
    # }})
    # job_q.post_job()
    from pprint import pprint
    # pprint(job_q.get_job())
    # pprint(job_q.job_id)
    # import time
    # time.sleep(10)
    # pprint(job_q.get_job())
    #
    # jobs = Jobs('http://mercury:9005')
    # pprint(jobs.get())
    ac = ActiveComputers('http://mercury:9005')
    pprint(ac.get())
    pprint(ac.query({'mercury_id': '017f3b1adc67a79050e3655747a0b6b0711c81ad68'}, projection=['mercury_id']))
