"""Exposes the full ``requests`` HTTP library API, while adding an extra
``family`` parameter to all HTTP request operations that may be used to restrict
the address family used when resolving a domain-name to an IP address.
"""

import os
import socket
import urllib.parse

import requests
import requests.adapters
import typing as ty
import urllib3  # type: ignore[import]
import urllib3.connection  # type: ignore[import]
import urllib3.exceptions  # type: ignore[import]
import urllib3.poolmanager  # type: ignore[import]
import urllib3.util.connection  # type: ignore[import]

AF2NAME = {
	int(socket.AF_INET):  "ip4",
	int(socket.AF_INET6): "ip6",
}
if hasattr(socket, "AF_UNIX"):
	AF2NAME[int(socket.AF_UNIX)] = "unix"
NAME2AF = {name: af for af, name in AF2NAME.items()}

PATCH_REQUESTS = (
	os.environ.get("PY_IPFS_HTTP_CLIENT_PATCH_REQUESTS", "yes").lower()
	not in ("false", "no")
)


# This function is copied from urllib3/util/connection.py (that in turn copied
# it from socket.py in the Python 2.7 standard library test suite) and accepts
# an extra `family` parameter that specifies the allowed address families for
# name resolution.
#
# The entire remainder of this file after this only exists to ensure that this
# `family` parameter is exposed all the way up to request's `Session` interface,
# storing it as part of the URL scheme while traversing most of the layers.
def create_connection(
		address: ty.Tuple[str, int],
		timeout: int = socket._GLOBAL_DEFAULT_TIMEOUT,  # type: ignore[attr-defined]
		source_address: ty.Optional[ty.Union[ty.Tuple[str, int], str, bytes]] = None,
		socket_options: ty.Optional[ty.List[ty.Tuple[int, int, ty.Union[int, bytes]]]] = None,
		family: int = socket.AF_UNSPEC
) -> socket.socket:
	host, port = address
	if host.startswith('['):
		host = host.strip('[]')
	err = None

	if not family or family == socket.AF_UNSPEC:
		family = urllib3.util.connection.allowed_gai_family()

	# Extension for Unix domain sockets
	if hasattr(socket, "AF_UNIX") and family == socket.AF_UNIX:
		gai_result: ty.Union[
			ty.List[
				ty.Tuple[
					socket.AddressFamily,
					socket.SocketKind,
					int,
					str,
					str
				]
			],
			ty.List[
				ty.Tuple[
					socket.AddressFamily,
					socket.SocketKind,
					int,
					str,
					ty.Union[
						ty.Tuple[str, int],
						ty.Tuple[str, int, int, int]
					]
				]
			]
		] = [(socket.AF_UNIX, socket.SOCK_STREAM, 0, "", host)]
	else:
		gai_result = socket.getaddrinfo(host, port, family, socket.SOCK_STREAM)

	for res in gai_result:
		af, socktype, proto, canonname, sa = res
		sock = None
		try:
			sock = socket.socket(af, socktype, proto)

			# If provided, set socket level options before connecting.
			if socket_options is not None and family != getattr(socket, "AF_UNIX", NotImplemented):
				for opt in socket_options:
					sock.setsockopt(*opt)

			if timeout is not socket._GLOBAL_DEFAULT_TIMEOUT:  # type: ignore[attr-defined]
				sock.settimeout(timeout)
			if source_address:
				sock.bind(source_address)
			sock.connect(sa)
			return sock
		except OSError as e:
			err = e
			if sock is not None:
				sock.close()

	if err is not None:
		raise err

	raise OSError("getaddrinfo returns an empty list")


# Override the `urllib3` low-level Connection objects that do the actual work
# of speaking HTTP
def _kw_scheme_to_family(
		kw: ty.Dict[str, ty.Any],
		base_scheme: str
) -> ty.Union[int, socket.AddressFamily]:
	family: ty.Union[int, socket.AddressFamily] = socket.AF_UNSPEC
	scheme = kw.pop("scheme", None)
	if isinstance(scheme, str):
		parts = scheme.rsplit("+", 1)
		if len(parts) == 2 and parts[0] == base_scheme:
			family = NAME2AF.get(parts[1], family)
	return family


class ConnectionOverrideMixin:
	def _new_conn(self) -> socket.socket:
		extra_kw = {
			"family": self.family  # type: ignore[attr-defined]
		}
		if self.source_address:  # type: ignore[attr-defined]
			extra_kw['source_address'] = self.source_address  # type: ignore[attr-defined]

		if self.socket_options:  # type: ignore[attr-defined]
			extra_kw['socket_options'] = self.socket_options  # type: ignore[attr-defined]

		try:
			dns_host = getattr(self, "_dns_host", self.host)  # type: ignore[attr-defined]
			if hasattr(socket, "AF_UNIX") and extra_kw["family"] == socket.AF_UNIX:
				dns_host = urllib.parse.unquote(dns_host)
			conn = create_connection(
				(dns_host, self.port), self.timeout, **extra_kw)  # type: ignore[attr-defined]
		except socket.timeout:
			raise urllib3.exceptions.ConnectTimeoutError(
				self, "Connection to %s timed out. (connect timeout=%s)" %
				(self.host, self.timeout))  # type: ignore[attr-defined]
		except OSError as e:
			raise urllib3.exceptions.NewConnectionError(
				self, "Failed to establish a new connection: %s" % e)

		return conn


class HTTPConnection(
		ConnectionOverrideMixin,
		urllib3.connection.HTTPConnection  # type: ignore[misc,no-any-unimported]
):
	def __init__(self, *args, **kw) -> None:  # type: ignore[no-untyped-def]
		self.family = _kw_scheme_to_family(kw, "http")
		super().__init__(*args, **kw)


class HTTPSConnection(
		ConnectionOverrideMixin,
		urllib3.connection.HTTPSConnection  # type: ignore[misc,no-any-unimported]
):
	def __init__(self, *args, **kw) -> None:  # type: ignore[no-untyped-def]
		self.family = _kw_scheme_to_family(kw, "https")
		super().__init__(*args, **kw)


# Override the higher-level `urllib3` ConnectionPool objects that instantiate
# one or more Connection objects and dispatch work between them
class HTTPConnectionPool(urllib3.HTTPConnectionPool):  # type: ignore[misc,no-any-unimported]
	ConnectionCls = HTTPConnection


class HTTPSConnectionPool(urllib3.HTTPSConnectionPool):  # type: ignore[misc,no-any-unimported]
	ConnectionCls = HTTPSConnection


# Override the highest-level `urllib3` PoolManager to also properly support the
# address family extended scheme values in URLs and pass these scheme values on
# to the individual ConnectionPool objects
class PoolManager(urllib3.PoolManager):  # type: ignore[misc,no-any-unimported]
	def __init__(self, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
		super().__init__(*args, **kwargs)
		
		# Additionally to adding our variant of the usual HTTP and HTTPS
		# pool classes, also add these for some variants of the default schemes
		# that are limited to some specific address family only
		self.pool_classes_by_scheme: ty.Dict[str, type] = {}
		for scheme, ConnectionPool in (("http", HTTPConnectionPool), ("https", HTTPSConnectionPool)):
			self.pool_classes_by_scheme[scheme] = ConnectionPool
			for name in AF2NAME.values():
				self.pool_classes_by_scheme["{0}+{1}".format(scheme, name)] = ConnectionPool
				self.key_fn_by_scheme["{0}+{1}".format(scheme, name)] = self.key_fn_by_scheme[scheme]

	# These next two are only required to ensure that our custom `scheme` values
	# will be passed down to the `*ConnectionPool`s and finally to the actual
	# `*Connection`s as parameter
	def _new_pool(
			self,
			scheme: str,
			host: str,
			port: int,
			request_context: ty.Optional[ty.Dict[str, ty.Any]] = None
	) -> ty.Union[HTTPConnectionPool, HTTPSConnectionPool]:
		# Copied from `urllib3` to *not* suppress the `scheme` parameter
		pool_cls = self.pool_classes_by_scheme[scheme]
		if request_context is None:
			request_context = self.connection_pool_kw.copy()
		
		for key in ('host', 'port'):
			request_context.pop(key, None)
		
		if scheme == "http" or scheme.startswith("http+"):
			for kw in urllib3.poolmanager.SSL_KEYWORDS:
				request_context.pop(kw, None)
		
		return ty.cast(
			ty.Union[HTTPConnectionPool, HTTPSConnectionPool],
			pool_cls(host, port, **request_context)
		)

	def connection_from_pool_key(
			self,
			pool_key: str,
			request_context: ty.Optional[ty.Dict[str, ty.Any]] = None
	) -> ty.Union[HTTPConnectionPool, HTTPSConnectionPool]:
		# Copied from `urllib3` so that we continue to ensure that this will
		# call `_new_pool`
		with self.pools.lock:
			pool: ty.Union[HTTPConnectionPool, HTTPSConnectionPool] = self.pools.get(pool_key)
			if pool:
				return pool

			if request_context is None:
				raise ValueError('request_context required')

			scheme = request_context['scheme']
			host = request_context['host']
			port = request_context['port']
			pool = self._new_pool(scheme, host, port, request_context=request_context)
			self.pools[pool_key] = pool
		return pool


# Override the lower-level `requests` adapter that invokes the `urllib3`
# PoolManager objects
class HTTPAdapter(requests.adapters.HTTPAdapter):
	def init_poolmanager(  # type: ignore[no-untyped-def]
			self,
			connections: int,
			maxsize: int,
			block: bool = False,
			**pool_kwargs
	) -> None:
		# save these values for pickling (copied from `requests`)
		self._pool_connections = connections
		self._pool_maxsize = maxsize
		self._pool_block = block

		self.poolmanager = PoolManager(num_pools=connections, maxsize=maxsize,
		                               block=block, strict=True, **pool_kwargs)


# Override the highest-level `requests` Session object to accept the `family`
# parameter for any request and encode its value as part of the URL scheme
# when passing it down to the adapter
class PatchedSession(requests.Session):
	def __init__(self) -> None:
		super().__init__()
		self.family = socket.AF_UNSPEC

		# Additionally to mounting our variant of the usual HTTP and HTTPS
		# adapter, also mount it for some variants of the default schemes that
		# are limited to some specific address family only
		adapter = HTTPAdapter()
		for scheme in ("http", "https"):
			self.mount("{0}://".format(scheme), adapter)
			for name in AF2NAME.values():
				self.mount("{0}+{1}://".format(scheme, name), adapter)

	@staticmethod
	def replace_scheme(family: int, url: str) -> str:
		if family == socket.AF_UNSPEC:
			return url
		else:
			# Inject provided address family value as extension to scheme
			parsed = urllib.parse.urlparse(url)
			parsed = parsed._replace(scheme="{0}+{1}".format(parsed.scheme, AF2NAME[int(family)]))
			return parsed.geturl()

	def request(  # type: ignore[override,no-untyped-def]
			self,
			method: str,
			url: str,
			*args,
			**kwargs
	) -> requests.Response:
		family = kwargs.pop("family", self.family)

		url = self.replace_scheme(family, url)

		return super().request(method, url, *args, **kwargs)


def wrapped_session() -> requests.Session:
	if PATCH_REQUESTS:
		return PatchedSession()
	else:
		return requests.Session()
