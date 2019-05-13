"""Test cases for http.py.

These tests are designed to mock http responses from the IPFS daemon. They
are used to determine if the functions in http.py are operating correctly.

Classes:
TestHttp -- A TCP client for interacting with an IPFS daemon
"""

import json
import time

import pytest
import pytest_localserver.http

import ipfshttpclient.http
import ipfshttpclient.exceptions



@pytest.fixture(scope="module")
def http_server(request):
	"""
	Slightly modified version of the ``pytest_localserver.plugin.http_server``
	fixture that will only start and stop the server application once for test
	performance reasons.
	"""
	server = pytest_localserver.http.ContentServer()
	server.start()
	request.addfinalizer(server.stop)
	return server


@pytest.fixture
def http_client(http_server):
	return ipfshttpclient.http.HTTPClient(
		"/ip4/{0}/tcp/{1}/http".format(*http_server.server_address),
		ipfshttpclient.DEFAULT_BASE
	)


def slow_http_server_app(environ, start_response):
	"""
	HTTP server application that will be slow to responsed (2 seconds)
	"""
	start_response("400 Bad Request", [
		("Content-Type", "text/json")
	])
	
	time.sleep(0.5)
	yield json.dumps({
		"Type": "error",
		"Message": "Timeout was not triggered"
	}).encode("utf-8")

@pytest.fixture(scope="module")
def slow_http_server(request):
	server = pytest_localserver.http.WSGIServer(application=slow_http_server_app)
	server.start()
	request.addfinalizer(server.stop)
	return server



def test_successful_request(http_client, http_server):
	"""Tests that a successful http request returns the proper message."""
	http_server.serve_content("okay", 200)
	
	res = http_client.request("/okay")
	assert res == b"okay"

def test_generic_failure(http_client, http_server):
	"""Tests that a failed http request raises an HTTPError."""
	http_server.serve_content("fail", 500)
	
	with pytest.raises(ipfshttpclient.exceptions.StatusError):
		http_client.request("/fail")

def test_http_client_failure(http_client, http_server):
	"""Tests that an http client failure raises an ipfsHTTPClientError."""
	http_server.serve_content(json.dumps({
		"Message": "Someone set us up the bomb"
	}), 500)
	
	with pytest.raises(ipfshttpclient.exceptions.ErrorResponse):
		http_client.request("/http_client_fail")

def test_http_client_late_failure(http_client, http_server):
	"""Tests that an http client failure raises an ipfsHTTPClientError."""
	http_server.serve_content(json.dumps({
		"Message": "okay"
	}) + "\n" + json.dumps({
		"Type":    "error",
		"Message": "request failed after all"
	}), 200)
	
	with pytest.raises(ipfshttpclient.exceptions.PartialErrorResponse):
		http_client.request("/http_client_fail_late", decoder="json")

def test_stream(http_client, http_server):
	"""Tests that the stream flag being set returns the raw response."""
	http_server.serve_content("okay", 200)
	
	res = http_client.request("/okay", stream=True)
	assert next(res) == b"okay"

def test_cat(http_client, http_server):
	"""Tests that paths ending in /cat are not parsed."""
	http_server.serve_content(json.dumps({
		"Message": "do not parse"
	}), 200)
	
	res = http_client.request("/cat")
	assert res == b'{"Message": "do not parse"}'

def test_default_decoder(http_client, http_server):
	"""Tests that the default encoding is set to json."""
	http_server.serve_content(json.dumps({
		"Message": "okay"
	}), 200)
	
	res = http_client.request("/http_client_okay")
	assert res == b'{"Message": "okay"}'

def test_explicit_decoder(http_client, http_server):
	"""Tests that an explicit decoder is handled correctly."""
	http_server.serve_content(json.dumps({
		"Message": "okay"
	}), 200)
	
	res = http_client.request("/http_client_okay", decoder="json")
	assert res[0]["Message"] == "okay"

def test_unsupported_decoder(http_client, http_server):
	"""Tests that unsupported encodings raise an exception."""
	http_server.serve_content(json.dumps({
		"Message": "Someone set us up the bomb"
	}), 500)
	
	with pytest.raises(ipfshttpclient.exceptions.EncoderMissingError):
		http_client.request("/http_client_fail", decoder="xyz")

def test_failed_decoder(http_client, http_server):
	"""Tests that a failed encoding parse raises an exception."""
	http_server.serve_content("okay", 200)
	
	with pytest.raises(ipfshttpclient.exceptions.DecodingError):
		http_client.request("/okay", decoder="json")

"""TODO: Test successful download
Need to determine correct way to mock an http request that returns a tar
file. tarfile.open expects the tar to be in the form of an octal escaped
string, but internal functionality keeps resulting in hexadecimal.
"""

def test_failed_download(http_client, http_server):
	"""Tests that a failed download raises an HTTPError."""
	http_server.serve_content("fail", 500)
	
	with pytest.raises(ipfshttpclient.exceptions.StatusError):
		http_client.download("/fail")

def test_download_timeout(slow_http_server):
	"""Tests that a timed-out download raises a TimeoutError."""
	http_client = ipfshttpclient.http.HTTPClient(
		"/ip4/{0}/tcp/{1}/http".format(*slow_http_server.server_address),
		ipfshttpclient.DEFAULT_BASE
	)
	
	with pytest.raises(ipfshttpclient.exceptions.TimeoutError):
		http_client.download('/timeout', timeout=0.1)

def test_request_timeout(slow_http_server):
	"""Tests that a timed-out request raises a TimeoutError."""
	http_client = ipfshttpclient.http.HTTPClient(
		"/ip4/{0}/tcp/{1}/http".format(*slow_http_server.server_address),
		ipfshttpclient.DEFAULT_BASE
	)
	
	with pytest.raises(ipfshttpclient.exceptions.TimeoutError):
		http_client.request('/timeout', timeout=0.1)

def test_session(http_client, http_server):
	"""Tests that a session is established and then closed."""
	http_server.serve_content("okay", 200)
	
	assert http_client._session is None
	try:
		http_client.open_session()
		http_client._session is not None
		res = http_client.request("/okay")
		assert res == b"okay"
	finally:
		http_client.close_session()
	assert http_client._session is None


def test_stream_close(mocker, http_client, http_server):
	mocker.patch("ipfshttpclient.http._notify_stream_iter_closed")
	http_server.serve_content("okay", 200)
	
	with http_client.request("/okay", stream=True) as response_iter:
		assert ipfshttpclient.http._notify_stream_iter_closed.call_count == 0
	assert ipfshttpclient.http._notify_stream_iter_closed.call_count == 1
	
	response_iter = http_client.request("/okay", stream=True)
	assert ipfshttpclient.http._notify_stream_iter_closed.call_count == 1
	response_iter.close()
	assert ipfshttpclient.http._notify_stream_iter_closed.call_count == 2
	
	http_client.request("/okay")
	assert ipfshttpclient.http._notify_stream_iter_closed.call_count == 3
