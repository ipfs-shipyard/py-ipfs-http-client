"""Test cases for http.py.

These tests are designed to mock http responses from the IPFS daemon. They
are used to determine if the functions in http.py are operating correctly.

Classes:
TestHttp -- A TCP client for interacting with an IPFS daemon
"""

import unittest
import json
import requests
import tarfile
import os
from httmock import urlmatch, HTTMock

import ipfsApi.http
import ipfsApi.exceptions


@urlmatch(netloc='localhost:5001', path=r'.*/okay')
def return_okay(url, request):
    """Defines an endpoint for successful http requests.

    This endpoint will listen at http://localhost:5001/*/okay for incoming
    requests and will always respond with a 200 status code and a Message of
    "okay".

    Keyword arguments:
    url -- the url of the incoming request
    request -- the request that is being responded to
    """
    return {
        'status_code': 200,
        'content': 'okay'.encode('utf-8'),
    }


@urlmatch(netloc='localhost:5001', path=r'.*/fail')
def return_fail(url, request):
    """Defines an endpoint for failed http requests.

    This endpoint will listen at http://localhost:5001/*/fail for incoming
    requests and will always respond with a 500 status code and a Message of
    "fail".

    Keyword arguments:
    url -- the url of the incoming request
    request -- the request that is being responded to
    """
    return {
        'status_code': 500,
        'content': 'fail'.encode('utf-8'),
    }


@urlmatch(netloc='localhost:5001', path=r'.*/apiokay')
def api_okay(url, request):
    """Defines an endpoint for successful api requests.

    This endpoint will listen at http://localhost:5001/*/apiokay for incoming
    requests and will always respond with a 200 status code and a json encoded
    Message of "okay".

    Keyword arguments:
    url -- the url of the incoming request
    request -- the request that is being responded to
    """
    return {
        'status_code': 200,
        'content': json.dumps({
            'Message': 'okay'}).encode('utf-8')
    }


@urlmatch(netloc='localhost:5001', path=r'.*/apifail')
def api_fail(url, request):
    """Defines an endpoint for failed api requests.

    This endpoint will listen at http://localhost:5001/*/apifail for incoming
    requests and will always respond with a 500 status code and a json encoded
    Message of "Someone set us up the bomb".

    Keyword arguments:
    url -- the url of the incoming request
    request -- the request that is being responded to
    """
    return {
        'status_code': 500,
        'content': json.dumps({
            'Message': 'Someone set us up the bomb'}).encode('utf-8')
    }


@urlmatch(netloc='localhost:5001', path=r'.*/cat')
def api_cat(url, request):
    """Defines an endpoint for a request to cat a file.

    This endpoint will listen at http://localhost:5001/*/cat for incoming
    requests and will always respond with a 200 status code and a json encoded
    Message of "do not parse".

    Keyword arguments:
    url -- the url of the incoming request
    request -- the request that is being responded to
    """
    return {
        'status_code': 200,
        'content': json.dumps({
            'Message': 'do not parse'}).encode('utf-8')
    }


class TestHttp(unittest.TestCase):
    """A series of tests to test the functionality of http.py.

    Public methods:
    setUp -- creates an instance of HTTPClient to test against
    test_successful_request -- tests that a successful http request returns the
                                proper message
    test_generic_failure -- tests that a failed http request raises an HTTPError
    test_api_failure -- tests that an api failure raises an ispfApiError
    test_stream -- tests that the stream flag being set returns the raw response
    test_cat -- tests that paths ending in /cat are not parsed
    test_default_decoder -- tests that the default encoding is set to json
    test_explicit_decoder -- tests that an explicit decoder is handled correctly
    test_unsupported_decoder -- tests that unsupported encodings raise an
                                EncodingException
    test_failed_decoder -- tests that a failed encoding parse returns response
                            text
    test_failed_download -- tests that a failed download raises an HTTPError
    test_session -- tests that a session is established and then closed
    """
    def setUp(self):
        """Creates an instance of HTTPClient to test against."""
        self.client = ipfsApi.http.HTTPClient(
            'localhost',
            5001,
            'api/v0',
            'json')

    def test_successful_request(self):
        """Tests that a successful http request returns the proper message."""
        with HTTMock(return_okay):
            res = self.client.request('/okay')
            self.assertEqual(res, 'okay')

    def test_generic_failure(self):
        """Tests that a failed http request raises an HTTPError."""
        with HTTMock(return_fail):
            self.assertRaises(requests.HTTPError,
                              self.client.request, '/fail')

    def test_api_failure(self):
        """Tests that an api failure raises an ispfApiError."""
        with HTTMock(api_fail):
            self.assertRaises(ipfsApi.exceptions.ipfsApiError,
                              self.client.request, '/apifail')

    def test_stream(self):
        """Tests that the stream flag being set returns the raw response."""
        with HTTMock(return_okay):
            res = self.client.request('/okay', stream=True)
            self.assertEqual(res.read(4), b'okay')

    def test_cat(self):
        """Tests that paths ending in /cat are not parsed."""
        with HTTMock(api_cat):
            res = self.client.request('/cat')
            self.assertEquals(res, '{"Message": "do not parse"}')

    def test_default_decoder(self):
        """Tests that the default encoding is set to json."""
        with HTTMock(api_okay):
            res = self.client.request('/apiokay')
            self.assertEquals(res['Message'], 'okay')

    def test_explicit_decoder(self):
        """Tests that an explicit decoder is handled correctly."""
        with HTTMock(api_okay):
            res = self.client.request('/apiokay',
                                      decoder='json')
            self.assertEquals(res['Message'], 'okay')

    def test_unsupported_decoder(self):
        """Tests that unsupported encodings raise an EncodingException."""
        with HTTMock(api_fail):
            self.assertRaises(ipfsApi.exceptions.EncodingException,
                              self.client.request, '/apifail', decoder='xyz')

    def test_failed_decoder(self):
        """Tests that a failed encoding parse returns response text."""
        with HTTMock(return_okay):
            res = self.client.request('/okay', decoder='json')
            self.assertEquals(res, 'okay')

    """TODO: Test successful download
    Need to determine correct way to mock an http request that returns a tar
    file. tarfile.open expects the tar to be in the form of an octal escaped
    string, but internal functionality keeps resulting in hexidecimal.
    """

    def test_failed_download(self):
        """Tests that a failed download raises an HTTPError."""
        with HTTMock(return_fail):
            self.assertRaises(requests.HTTPError,
                              self.client.download, '/fail')

    def test_session(self):
        """Tests that a session is established and then closed."""
        with HTTMock(return_okay):
            with self.client.session():
                res = self.client.request('/okay')
                self.assertEqual(res, 'okay')
            self.assertEqual(self.client._session, None)
