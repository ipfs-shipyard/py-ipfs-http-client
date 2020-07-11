"""Default HTTP client selection proxy"""
import os

from .http_common import (
	StreamDecodeIteratorSync,
	
	addr_t, auth_t, cookies_t, headers_t, params_t, reqdata_sync_t, timeout_t,
	workarounds_t,
)


__all__ = (
	"addr_t", "auth_t", "cookies_t", "headers_t", "params_t", "reqdata_sync_t",
	"timeout_t", "workarounds_t",
	
	"ClientSync",
	"StreamDecodeIteratorSync",
)

PREFER_HTTPX = (os.environ.get("PY_IPFS_HTTP_CLIENT_PREFER_HTTPX", "no").lower()
                not in ("0", "f", "false", "n", "no"))
if PREFER_HTTPX:  # pragma: http-backend=httpx
	try:  #PY36+
		from . import http_httpx as _backend
	except (ImportError, SyntaxError):  #PY35
		from . import http_requests as _backend  # type: ignore[no-redef]
else:  # pragma: http-backend=requests
	try:
		from . import http_requests as _backend  # type: ignore[no-redef]
	except ImportError:  # pragma: no cover
		from . import http_httpx as _backend

ClientSync = _backend.ClientSync