
import json
import requests


def check_error(f):
    """Decorator provides consistent formatting for client http errors."""
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
