# Only add tests to this file if they really are specific to the behaviour
# of this backend. For cross-backend or `http_common.py` tests use
# `test_http.py` instead.
import http.cookiejar
import math
import sys

import pytest

if sys.version_info <= (3, 6):
	pytest.skip("HTTPx requires Python 3.6+", allow_module_level=True)
pytest.importorskip("ipfshttpclient.http_httpx")
import ipfshttpclient.http_httpx


def generator():
	yield b"bla"
generator_instance = generator()

cookiejar = http.cookiejar.CookieJar()

@pytest.mark.parametrize("kwargs,expected", [
	({}, {}),
	
	({
		"auth": ("user", "pass"),
		"data": generator_instance,
		"cookies": cookiejar,
		"headers": {"name": "value"},
		"params": (("name", "value"),),
		"timeout": (math.inf, math.inf),
	}, {
		"auth": ("user", "pass"),
		"data": generator_instance,
		"cookies": cookiejar,
		"headers": {"name": "value"},
		"params": (("name", "value"),),
		"timeout": (None, None),
	}),
	
	({
		"auth": ("user", b"pass"),
		"data": (b"abc", b"def"),
		"cookies": {"name": "value"},
		"headers": ((b"name", b"value"),),
		"timeout": 34,
	}, {
		"auth": ("user", b"pass"),
		"data": (b"abc", b"def"),
		"cookies": {"name": "value"},
		"headers": ((b"name", b"value"),),
		"timeout": 34,
	}),
])
def test_map_args_to_httpx(kwargs, expected):
	assert ipfshttpclient.http_httpx.map_args_to_httpx(**kwargs) == expected

@pytest.mark.parametrize("args,kwargs,expected", [
	(("/dns/localhost/tcp/5001/http", "api/v0"), {}, {
		"base_url": "http://localhost:5001/api/v0/",
		"params": [("stream-channels", "true")],
	}),
	
	(("/dns6/ietf.org/tcp/443/https", "/base/"), {
		"auth": ("user", "pass"),
		"cookies": cookiejar,
		"headers": {"name": "value"},
		"offline": True,
		"timeout": (math.inf, math.inf),
	}, {
		#XXX: This should also store the expected address family somewhere
		"base_url": "https://ietf.org:443/base/",
		"auth": ("user", "pass"),
		"cookies": cookiejar,
		"headers": {"name": "value"},
		"params": [("offline", "true"), ("stream-channels", "true")],
		"timeout": (None, None),
	}),
])
def test_client_args_to_session_kwargs(args, kwargs, expected):
	client = ipfshttpclient.http_httpx.ClientSync(*args, **kwargs)
	assert client._session_kwargs == expected