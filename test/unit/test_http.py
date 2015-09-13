import unittest
import json
import requests
from httmock import urlmatch, HTTMock

import ipfsApi.http
import ipfsApi.exceptions


@urlmatch(netloc='localhost:5001', path=r'.*/okay')
def return_okay(url, request):
    return {
        'status_code': 200,
        'content': 'okay'.encode('utf-8'),
    }


@urlmatch(netloc='localhost:5001', path=r'.*/fail')
def return_fail(url, request):
    return {
        'status_code': 500,
        'content': 'fail'.encode('utf-8'),
    }


@urlmatch(netloc='localhost:5001', path=r'.*/apiokay')
def api_okay(url, request):
    return {
        'status_code': 200,
        'content': json.dumps({
            'Message': 'okay'}).encode('utf-8')
    }

@urlmatch(netloc='localhost:5001', path=r'.*/apifail')
def api_fail(url, request):
    return {
        'status_code': 500,
        'content': json.dumps({
            'Message': 'Someone set us up the bomb'}).encode('utf-8')
    }


class TestHttp(unittest.TestCase):
    def setUp(self):
        self.client = ipfsApi.http.HTTPClient(
            'localhost',
            5001,
            'api/v0',
            'json')

    def test_successful_request(self):
        with HTTMock(return_okay):
            res = self.client.request('/okay')
            self.assertEqual(res, 'okay')

    def test_generic_failure(self):
        with HTTMock(return_fail):
            self.assertRaises(requests.HTTPError,
                              self.client.request, '/fail')

    def test_api_failure(self):
        with HTTMock(api_fail):
            self.assertRaises(ipfsApi.exceptions.ipfsApiError,
                              self.client.request, '/apifail')

    def test_session(self):
        with HTTMock(return_okay):
            with self.client.session():
                res = self.client.request('/okay')
                self.assertEqual(res, 'okay')

    def test_explicit_decoder(self):
        with HTTMock(api_okay):
            res = self.client.request('/apiokay',
                                      decoder='json')
            self.assertEquals(res['Message'], 'okay')
