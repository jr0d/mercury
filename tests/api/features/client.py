import copy
import requests

class APIClient(object):

    def __init__(self, base_url, request_kwargs=None):

        timeout = None
        ssl_certificate_verify = False
        verbose = True

        if request_kwargs:
            timeout = request_kwargs.get('timeout', timeout)
            ssl_certificate_verify = request_kwargs.get(
                'ssl_certificate_verify', ssl_certificate_verify)
            verbose = request_kwargs.get('verbose', verbose)

        self.base_url = base_url
        self.headers = {'Content-Type': 'application/json'}

        self.verify = ssl_certificate_verify
        self.verbose = verbose

        self.request_kwargs = dict()
        self.request_kwargs['url'] = self.base_url
        self.request_kwargs['headers'] = self.headers
        self.request_kwargs['verify'] = self.verify

        if timeout:
            self.request_kwargs['timeout'] = timeout

    def get(self, resource_id=None, params=None, url=None):
        request_kwargs = copy.deepcopy(self.request_kwargs)
        if url:
            request_kwargs['url'] = url
        if resource_id:
            resource_url = request_kwargs['url']
            request_kwargs['url'] = '{0}/{1}'.format(resource_url, resource_id)
        if params:
           request_kwargs['params'] = params
        resp = requests.get(**request_kwargs)
        if self.verbose:
            print('{0}GET REQUEST{1}'.format('*' * 20, '*' * 24))
            print(request_kwargs)
            print('{0}RESPONSE{1}'.format('*' * 20, '*' * 27))
            print(resp.content)
            print('*' * 48)
        return resp

    def post(self, data, url_suffix=None):
        request_kwargs = copy.deepcopy(self.request_kwargs)
        if url_suffix:
            resource_url = request_kwargs['url']
            request_kwargs['url'] = '{0}/{1}'.format(resource_url, url_suffix)
        request_kwargs['data'] = data
        resp = requests.post(**request_kwargs)
        if self.verbose:
            print('{0}GET REQUEST{1}'.format('*' * 20, '*' * 24))
            print(request_kwargs)
            print('{0}RESPONSE{1}'.format('*' * 20, '*' * 27))
            print(resp.content)
            print('*' * 48)
        return resp
