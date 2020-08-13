# Only add tests to this file if they really are specific to the behaviour
# of this backend. For cross-backend or `http_common.py` tests use
# `test_http.py` instead.
import http.cookiejar
import math
import socket

import pytest

pytest.importorskip("ipfshttpclient.http_requests")
import ipfshttpclient.http_requests


cookiejar = http.cookiejar.CookieJar()

@pytest.mark.parametrize("kwargs,expected", [
	({}, {}),
	
	({
		"auth": ("user", "pass"),
		"cookies": cookiejar,
		"headers": {"name": "value"},
		"params": (("name", "value"),),
		"timeout": (math.inf, math.inf),
	}, {
		"auth": ("user", "pass"),
		"cookies": cookiejar,
		"headers": {"name": "value"},
		"params": {"name": "value"},
		"timeout": (None, None),
	}),
	
	({
		"auth": ("user", b"pass"),
		"cookies": {"name": "value"},
		"headers": ((b"name", b"value"),),
		"timeout": 34,
	}, {
		"auth": ("user", b"pass"),
		"cookies": {"name": "value"},
		"headers": ((b"name", b"value"),),
		"timeout": 34,
	}),
])
def test_map_args_to_requests(kwargs, expected):
	assert ipfshttpclient.http_requests.map_args_to_requests(**kwargs) == expected

@pytest.mark.parametrize("args,kwargs,expected1,expected2,expected3", [
	(("/dns/localhost/tcp/5001/http", "api/v0"), {}, "http://localhost:5001/api/v0/", {
		"family": socket.AF_UNSPEC,
		"params": {'stream-channels': 'true'},
	}, None),
	
	(("/dns6/ietf.org/tcp/443/https", "/base/"), {
		"auth": ("user", "pass"),
		"cookies": cookiejar,
		"headers": {"name": "value"},
		"offline": True,
		"timeout": (math.inf, math.inf),
	}, "https://ietf.org:443/base/", {
		"family": socket.AF_INET6,
		"auth": ("user", "pass"),
		"cookies": cookiejar,
		"headers": {"name": "value"},
		"params": {'offline': 'true', 'stream-channels': 'true'},
	}, (math.inf, math.inf)),
])
def test_client_args_to_session_props(args, kwargs, expected1, expected2, expected3):
	client = ipfshttpclient.http_requests.ClientSync(*args, **kwargs)
	assert client._base_url == expected1
	assert client._session_props == expected2
	assert client._default_timeout == expected3