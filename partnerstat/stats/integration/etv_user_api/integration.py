#!/usr/bin/env python
# -*- coding: utf-8 -*-

from urllib.request import urlopen
import urllib.request, urllib, base64
from urllib.parse import urljoin
import urllib.parse
import json

try:
    from django.conf import settings
    BASE_API_URL = getattr(settings, 'WEBSITE_API_ENDPOINT')
    django_env = True
except ImportError:
    django_env = False


class HTTPCient(object):

    base_url = getattr(settings, 'WEBSITE_API_ENDPOINT', None) if django_env else None
    auth_id = getattr(settings, 'WEBSITE_API_AUTENTICATION_USER_ID', None) if django_env else None
    auth_secret = getattr(settings, 'WEBSITE_API_CRM_AUTHENTICATION_USER_SECRET', None) if django_env else None

    def __init__(self):
        if self.base_url is None:
            raise Exception('Please provide `BASE_API_URL` to client')
        if self.auth_id is None or self.auth_secret is None:
            raise Exception('Please provide credentials, specefy them in settings file or '
                            'set appropriate attributes to client instance')

    def request(self, path, method=None, data=None, *a, **k):

            url = urljoin(self.base_url, path)

            if data is not None:
                if method in ['POST', 'PUT']:
                    data = json.dumps(data)
                    params =  {'Content-Type': 'application/json'}
                else:
                    data = urllib.urlencode(data)
                    params = {}
                req = urllib.request.Request(url, data, params)
            else:
                req = urllib.request.Request(url)

            if method is not None:
                req.get_method = lambda: method

            req = self.auth(req)

            try:
                connection = urlopen(req)
                resp = connection.read()
                connection.close()
                status = 200
            except urllib.error.HTTPError as err:

                if err.code == 400:
                    resp = err.read()
                    status = err.code
                else:
                    raise

            jresp = json.loads(resp.decode("utf-8"))

            if isinstance(jresp, dict):
                jresp['status'] = status
            return jresp

    def auth(self, request):

        base64string = base64.b64encode(bytearray('%s:%s' % (self.auth_id, self.auth_secret), 'utf-8')).decode('utf8').replace('\n', '')
        request.add_header("Authorization", "Basic %s" % base64string)
        return request


class BaseResourceClient(object):

    per_page = 30

    resource_url = ''

    client = HTTPCient()

    default_params = {'per_page': per_page, 'page': 1}

    def get_params(self, **kwargs):

        print('!!!')
        # return dict(self.default_params.items() + kwargs.items())

        d = self.default_params.copy()
        d.update(kwargs)

        print(d)

        return d

    def get_url(self, **kwargs):
        url = urljoin(self.client.base_url, self.resource_url)
        if kwargs:
            url = self.add_parameters_to_url(url, **kwargs)
        return url

    def add_parameters_to_url(self, url, **kwargs):
        for key, val in self.get_params(**kwargs).items():
            if val is not None:
                val = str(val) if isinstance(val, int) else val.encode('utf-8')
                delimeter = '&' if '?' in url else '?'
                url = url + delimeter + '%s=%s' % (key, urllib.parse.quote(val))
        return url

    def get_object_url(self, obj_id, **kwargs):
        url = urljoin(self.get_url() + '/', str(obj_id))
        if kwargs:
            url = self.add_parameters_to_url(url, **kwargs)
        return url

    def get_objects(self, **kwargs):
        return self.client.request(self.get_url(**kwargs))

    def get_one_object(self, obj_id, **kwargs):
        url = self.get_object_url(obj_id, **kwargs)
        return self.client.request(url)

    def update(self, obj_id, data={}):
        url = self.get_object_url(obj_id)
        data = self.alter_data(data)
        return self.client.request(url, data=data, method="PUT")

    def create(self, data={}):
        url = self.get_url()
        data = self.alter_data(data)
        return self.client.request(url, data=data, method="POST")

    def alter_data(self, data):
        return data


class RelatedResourceBase(BaseResourceClient):
    user_id = None

    def set_user_id(self, uid):
        if isinstance(uid, int):
            self.user_id = uid
        else:
            raise Exception('User suppose tube and instance of int type')

    def get_url(self, **kwargs):
        if self.user_id is not None:
            bae_url = '%susers/%s/' % (self.client.base_url,  str(self.user_id))
        else:
            raise Exception('Set user id for resource!')

        url = urljoin(bae_url , self.resource_url)

        if kwargs:
            url = self.add_parameters_to_url(url, **kwargs)
        return url