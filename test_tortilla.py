#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import json
import time
import unittest

import httpretty
import tortilla
import six


API_URL = 'https://test.tortilla.locally'
api = tortilla.wrap(API_URL)


def register_urls(endpoints):
    for endpoint, options in six.iteritems(endpoints):
        if isinstance(options['body'], (dict, list, tuple)):
            body = json.dumps(options['body'])
        else:
            body = options['body']
        httpretty.register_uri(method=options.get('method', 'GET'),
                               status=options.get('status', 200),
                               uri=API_URL + endpoint,
                               body=body)


with open('test_data.json') as resource:
    test_data = json.load(resource)
endpoints = test_data['endpoints']
register_urls(endpoints)


httpretty.register_uri(
    httpretty.GET, API_URL + '/cache',
    responses=[
       httpretty.Response(body='"cache this response"'),
       httpretty.Response(body='"this should not be returned"'),
    ]
)


class TestTortilla(unittest.TestCase):

    def test_json_response(self):
        assert api.user.get('jimmy') == endpoints['/user/jimmy']['body']
        assert api.user.get('имя') == endpoints['/user/имя']['body']

    def test_non_json_response(self):
        self.assertRaises(ValueError, api.nojson.get)
        assert api.nojson.get(silent=True) is None

    def test_formed_urls(self):
        assert api.this.url() == API_URL + '/this'
        assert api('this').url() == API_URL + '/this'
        assert api.this('that').url() == API_URL + '/this/that'
        assert api('this')('that').url() == API_URL + '/this/that'
        assert api.user('имя').url() == API_URL + '/user/имя'

    def test_cached_response(self):
        api.cache.get(cache_lifetime=100)
        assert api.cache.get() == "cache this response"
        api.cache.get(cache_lifetime=0.25, overwrite_cache=True)
        time.sleep(0.5)
        assert api.cache.get() == "this should not be returned"


if __name__ == '__main__':
    httpretty.enable()
    unittest.main()
    httpretty.disable()
