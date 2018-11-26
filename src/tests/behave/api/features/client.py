import copy
import json
import requests
import datetime
from src.tests.behave.common.config import get_conflagration


class APIClient(object):
    def __init__(self, base_url, request_kwargs=None, client_kwargs=None):

        self.cfg = get_conflagration()
        token = self.get_identity_token()

        timeout = None
        ssl_certificate_verify = False
        verbose = True

        if request_kwargs:
            timeout = request_kwargs.get("timeout", timeout)
            ssl_certificate_verify = request_kwargs.get(
                "ssl_certificate_verify", ssl_certificate_verify
            )
            verbose = request_kwargs.get("verbose", verbose)

        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json",
            "X-Auth-Token": token,
        }

        if client_kwargs:
            if not client_kwargs["authorized"]:
                self.headers["X-Auth-Token"] = ""

        self.verify = ssl_certificate_verify
        self.verbose = verbose

        self.request_kwargs = dict()
        self.request_kwargs["url"] = self.base_url
        self.request_kwargs["headers"] = self.headers
        self.request_kwargs["verify"] = self.verify

        if timeout:
            self.request_kwargs["timeout"] = timeout

    def get(
        self,
        resource_id=None,
        params=None,
        url=None,
        url_suffix=None,
        headers=None,
    ):
        request_kwargs = copy.deepcopy(self.request_kwargs)
        if url:
            request_kwargs["url"] = url
        if resource_id:
            resource_url = request_kwargs["url"]
            request_kwargs["url"] = "{0}/{1}".format(resource_url, resource_id)
        if url_suffix:
            resource_url = request_kwargs["url"]
            request_kwargs["url"] = "{0}/{1}".format(resource_url, url_suffix)
        if params:
            request_kwargs["params"] = params
        if headers:
            request_kwargs["headers"].update(headers)
        resp = requests.get(**request_kwargs)
        if self.verbose:
            d = datetime.datetime.now()
            s = "{}-{}-{} {}:{}:{}".format(
                d.year, d.month, d.day, d.hour, d.minute, d.second
            )
            print("{0}GET REQUEST{1}".format("*" * 20, "*" * 24))
            print("{0}{1}{2}".format("*" * 16, s, "*" * 20))
            print(request_kwargs)
            print("{0}RESPONSE{1}".format("*" * 20, "*" * 27))
            print(resp.content)
            print("*" * 48)
        return resp

    def post(self, data, url_suffix=None, headers=None, resource_id=None):
        request_kwargs = copy.deepcopy(self.request_kwargs)
        if resource_id:
            resource_url = request_kwargs["url"]
            request_kwargs["url"] = "{0}/{1}".format(resource_url, resource_id)
        if url_suffix:
            resource_url = request_kwargs["url"]
            request_kwargs["url"] = "{0}/{1}".format(resource_url, url_suffix)
        if headers:
            request_kwargs["headers"].update(headers)
        request_kwargs["data"] = data
        resp = requests.post(**request_kwargs)
        if self.verbose:
            d = datetime.datetime.now()
            s = "{}-{}-{} {}:{}:{}".format(
                d.year, d.month, d.day, d.hour, d.minute, d.second
            )
            print("{0}POST REQUEST{1}".format("*" * 20, "*" * 24))
            print("{0}{1}{2}".format("*" * 16, s, "*" * 21))
            print(request_kwargs)
            print("{0}RESPONSE{1}".format("*" * 20, "*" * 27))
            print(resp.content)
            print("*" * 48)
        return resp

    def delete(self, url_suffix=None, headers=None, resource_id=None):
        request_kwargs = copy.deepcopy(self.request_kwargs)
        if resource_id:
            resource_url = request_kwargs["url"]
            request_kwargs["url"] = "{0}/{1}".format(resource_url, resource_id)
        if url_suffix:
            resource_url = request_kwargs["url"]
            request_kwargs["url"] = "{0}/{1}".format(resource_url, url_suffix)
        if headers:
            request_kwargs["headers"].update(headers)
        resp = requests.delete(**request_kwargs)
        if self.verbose:
            d = datetime.datetime.now()
            s = "{}-{}-{} {}:{}:{}".format(
                d.year, d.month, d.day, d.hour, d.minute, d.second
            )
            print("{0}DELETE REQUEST{1}".format("*" * 20, "*" * 24))
            print("{0}{1}{2}".format("*" * 18, s, "*" * 21))
            print(request_kwargs)
            print("{0}RESPONSE{1}".format("*" * 20, "*" * 27))
            print(resp.content)
            print("*" * 48)
        return resp

    def get_identity_token(self):
        internal_idenity_url = self.cfg.INTERNAL_IDENTITY.internal_identity_url
        internal_identity_username = (
            self.cfg.INTERNAL_IDENTITY.internal_identity_username
        )
        internal_identity_password = (
            self.cfg.INTERNAL_IDENTITY.internal_identity_password
        )
        domain = self.cfg.INTERNAL_IDENTITY.domain
        domain_name = self.cfg.INTERNAL_IDENTITY.domain_name
        identity_headers = {"Content-Type": "application/json"}
        identity_data = {
            "auth": {
                "passwordCredentials": {
                    "username": internal_identity_username,
                    "password": internal_identity_password,
                },
                domain: {"name": domain_name},
            }
        }
        token_resp = requests.post(
            internal_idenity_url,
            headers=identity_headers,
            data=json.dumps(identity_data),
        )
        token = token_resp.json()["access"]["token"]["id"]
        return token
