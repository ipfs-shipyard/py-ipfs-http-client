"""Test cases for http.py.

These tests are designed to mock http responses from the IPFS daemon. They
are used to determine if the functions in http.py are operating correctly.

Classes:
TestHttp -- A TCP client for interacting with an IPFS daemon
"""

import json
import tarfile
import os

from httmock import urlmatch, HTTMock
import pytest
import requests

import ipfshttpclient.http
import ipfshttpclient.exceptions


HOST = "localhost"
PORT = 5001
NETLOC = "{0}:{1}".format(HOST, PORT)


@pytest.fixture
def http_client():
	return ipfshttpclient.http.HTTPClient(
		HOST, PORT, ipfshttpclient.DEFAULT_BASE
	)


@urlmatch(netloc=NETLOC, path=r".*/okay")
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
		"status_code": 200,
		"content": "okay".encode("utf-8"),
	}


@urlmatch(netloc=NETLOC, path=r".*/fail")
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
		"status_code": 500,
		"content": "fail".encode("utf-8"),
	}


@urlmatch(netloc=NETLOC, path=r".*/http_client_okay")
def http_client_okay(url, request):
	"""Defines an endpoint for successful http client requests.

	This endpoint will listen at http://localhost:5001/*/http_client_okay for incoming
	requests and will always respond with a 200 status code and a json encoded
	Message of "okay".

	Keyword arguments:
	url -- the url of the incoming request
	request -- the request that is being responded to
	"""
	return {
		"status_code": 200,
		"content": json.dumps({
			"Message": "okay"
		}).encode("utf-8")
	}


@urlmatch(netloc=NETLOC, path=r".*/http_client_fail")
def http_client_fail(url, request):
	"""Defines an endpoint for failed http client requests.

	This endpoint will listen at http://localhost:5001/*/http_client_fail for incoming
	requests and will always respond with a 500 status code and a json encoded
	Message of "Someone set us up the bomb".

	Keyword arguments:
	url -- the url of the incoming request
	request -- the request that is being responded to
	"""
	return {
		"status_code": 500,
		"content": json.dumps({
			"Message": "Someone set us up the bomb"
		}).encode("utf-8")
	}



@urlmatch(netloc=NETLOC, path=r'.*/http_client_fail_late')
def http_client_fail_late(url, request):
	"""Defines an endpoint for successful http client requests.

	This endpoint will listen at http://localhost:5001/*/http_client_fail_late
	for incoming requests and will always respond with a 200 status code, a
	json encoded Message of "okay", followed by a late error message.

	Keyword arguments:
	url -- the url of the incoming request
	request -- the request that is being responded to
	"""
	return {
		"status_code": 200,
		"content": json.dumps({
			"Message": "okay"
		}).encode("utf-8") + b"\n" + json.dumps({
			"Type":    "error",
			"Message": "request failed after all"
		}).encode("utf-8")
	}

@urlmatch(netloc=NETLOC, path=r".*/cat")
def http_client_cat(url, request):
	"""Defines an endpoint for a request to cat a file.

	This endpoint will listen at http://localhost:5001/*/cat for incoming
	requests and will always respond with a 200 status code and a json encoded
	Message of "do not parse".

	Keyword arguments:
	url -- the url of the incoming request
	request -- the request that is being responded to
	"""
	return {
		"status_code": 200,
		"content": json.dumps({
			"Message": "do not parse"
		}).encode("utf-8")
	}


def test_successful_request(http_client):
	"""Tests that a successful http request returns the proper message."""
	with HTTMock(return_okay):
		res = http_client.request("/okay")
		assert res == b"okay"

def test_generic_failure(http_client):
	"""Tests that a failed http request raises an HTTPError."""
	with HTTMock(return_fail):
		with pytest.raises(ipfshttpclient.exceptions.StatusError):
			http_client.request("/fail")

def test_http_client_failure(http_client):
	"""Tests that an http client failure raises an ipfsHTTPClientError."""
	with HTTMock(http_client_fail):
		with pytest.raises(ipfshttpclient.exceptions.ErrorResponse):
			http_client.request("/http_client_fail")

def test_http_client_late_failure(http_client):
	"""Tests that an http client failure raises an ipfsHTTPClientError."""
	with HTTMock(http_client_fail_late):
		with pytest.raises(ipfshttpclient.exceptions.PartialErrorResponse):
			http_client.request("/http_client_fail_late", decoder="json")

def test_stream(http_client):
	"""Tests that the stream flag being set returns the raw response."""
	with HTTMock(return_okay):
		res = http_client.request("/okay", stream=True)
		assert next(res) == b"okay"

def test_cat(http_client):
	"""Tests that paths ending in /cat are not parsed."""
	with HTTMock(http_client_cat):
		res = http_client.request("/cat")
		assert res == b'{"Message": "do not parse"}'

def test_default_decoder(http_client):
	"""Tests that the default encoding is set to json."""
	with HTTMock(http_client_okay):
		res = http_client.request("/http_client_okay")
		assert res == b'{"Message": "okay"}'

def test_explicit_decoder(http_client):
	"""Tests that an explicit decoder is handled correctly."""
	with HTTMock(http_client_okay):
		res = http_client.request("/http_client_okay", decoder="json")
		assert res[0]["Message"] == "okay"

def test_unsupported_decoder(http_client):
	"""Tests that unsupported encodings raise an exception."""
	with HTTMock(http_client_fail):
		with pytest.raises(ipfshttpclient.exceptions.EncoderMissingError):
			http_client.request("/http_client_fail", decoder="xyz")

def test_failed_decoder(http_client):
	"""Tests that a failed encoding parse raises an exception."""
	with HTTMock(return_okay):
		with pytest.raises(ipfshttpclient.exceptions.DecodingError):
			http_client.request("/okay", decoder="json")

"""TODO: Test successful download
Need to determine correct way to mock an http request that returns a tar
file. tarfile.open expects the tar to be in the form of an octal escaped
string, but internal functionality keeps resulting in hexadecimal.
"""

def test_failed_download(http_client):
	"""Tests that a failed download raises an HTTPError."""
	with HTTMock(return_fail):
		with pytest.raises(ipfshttpclient.exceptions.StatusError):
			http_client.download("/fail")

def test_session(http_client):
	"""Tests that a session is established and then closed."""
	with HTTMock(return_okay):
		with http_client.session():
			res = http_client.request("/okay")
			assert res == b"okay"
		assert http_client._session is None


def test_stream_close(mocker):
	client = ipfshttpclient.http.HTTPClient("localhost", 5001, "api/v0")
	mocker.patch("ipfshttpclient.http._notify_stream_iter_closed")
	with HTTMock(return_okay):
		with client.request("/okay", stream=True) as response_iter:
			assert ipfshttpclient.http._notify_stream_iter_closed.call_count == 0
		assert ipfshttpclient.http._notify_stream_iter_closed.call_count == 1

		response_iter = client.request("/okay", stream=True)
		assert ipfshttpclient.http._notify_stream_iter_closed.call_count == 1
		response_iter.close()
		assert ipfshttpclient.http._notify_stream_iter_closed.call_count == 2

		client.request("/okay")
		assert ipfshttpclient.http._notify_stream_iter_closed.call_count == 3
