import json
import requests


class Job(object):
    JOBS_URI = 'api/rpc/jobs'

    def __init__(self, rpc_service_url, query, instruction):
        self.rpc_service_url = rpc_service_url
        self.query = query
        self.instruction = instruction

        self.job_id = None
        self.response_data = None
        self.base_url = '{0}/{1}'.format(self.rpc_service_url, self.JOBS_URI)

    def join_url(self, addition):
        return self.base_url + '/' + addition.lstrip('/')

    def post_job(self):
        _payload = {
            'query': self.query,
            'instruction': self.instruction
        }
        r = requests.post(self.base_url, data=json.dumps(_payload), headers={'Content-type': 'application/json'})
        r.raise_for_status()

        self.job_id = r.json()['job_id']

    def get_job(self):
        if not self.job_id:
            return

        r = requests.get(self.join_url(self.job_id))
        r.raise_for_status()
        return r.json()


if __name__ == '__main__':
    job = Job('http://localhost:9005', {}, {'method': 'run', 'args': ['cat /etc/redhat-release']})
    job.post_job()
    from pprint import pprint
    pprint(job.get_job())
    pprint(job.job_id)
    import time
    time.sleep(10)
    pprint(job.get_job())
