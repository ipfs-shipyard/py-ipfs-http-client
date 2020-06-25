"""HTTP client for api requests.

This is pluggable into the IPFS Api client and will hopefully be supplemented
by an asynchronous version.
"""

import abc
import functools
import http.client
import math
import os
import socket
import tarfile
import typing as ty
import urllib.parse

import multiaddr
from multiaddr.protocols import (P_DNS, P_DNS4, P_DNS6, P_HTTP, P_HTTPS, P_IP4, P_IP6, P_TCP)

from . import encoding
from . import exceptions
from . import utils
PATCH_REQUESTS = (os.environ.get("PY_IPFS_HTTP_CLIENT_PATCH_REQUESTS", "yes").lower()
                  not in ("false", "no"))
if PATCH_REQUESTS:
	from . import requests_wrapper as requests
else:  # pragma: no cover (always enabled in production)
	import requests

T_co = ty.TypeVar("T_co", covariant=True)

addr_t = ty.Union[multiaddr.Multiaddr, bytes, str]
auth_t = ty.Optional[ty.Tuple[ty.Union[str, bytes], ty.Union[str, bytes]]]
cookies_t = ty.Optional[ty.Union[
	"http.cookiejar.CookieJar",
	ty.Dict[str, str]
]]
headers_t = ty.Dict[str, str]
params_t = ty.Optional[ty.Sequence[ty.Tuple[str, str]]]
reqdata_sync_t = ty.Optional[ty.Iterator[bytes]]
timeout_t = ty.Optional[ty.Union[
	float,
	ty.Tuple[float, float],
]]
workarounds_t = ty.Optional[ty.Set[str]]


def pass_defaults(func):
	"""Decorator that returns a function named wrapper.

	When invoked, wrapper invokes func with default kwargs appended.

	Parameters
	----------
	func : callable
		  The function to append the default kwargs to
	"""
	@functools.wraps(func)
	def wrapper(self, *args, **kwargs):
		merged = {}
		merged = utils.deep_update(merged, self.defaults)
		merged = utils.deep_update(merged, kwargs)
		return func(self, *args, **merged)
	return wrapper


def _notify_stream_iter_closed():
	pass  # Mocked by unit tests to determine check for proper closing


class StreamDecodeIterator(ty.Generic[T_co]):
	"""
	Wrapper around `Iterable` that allows the iterable to be used in a
	context manager (`with`-statement) allowing for easy cleanup.
	"""
	def __init__(self, response: requests.Response, parser: encoding.Encoding[T_co]):
		response_iter = response.iter_content(chunk_size=None)
		
		self._response = response  # type: ty.Optional[requests.Response]
		self._parser   = parser  # type: ty.Optional[encoding.Encoding[T_co]]
		self._response_iter = response_iter  # type: ty.Optional[ty.Generator[bytes, ty.Any, ty.Any]]
		self._parser_iter   = None  # type: ty.Optional[ty.Generator[bytes, ty.Any, ty.Any]]

	def __iter__(self) -> "StreamDecodeIterator[T_co]":
		return self

	def __next__(self) -> T_co:
		while True:
			# Try reading for current parser iterator
			if self._parser_iter is not None:
				try:
					result = next(self._parser_iter)  # type: T_co
					
					# Detect late error messages that occured after some data
					# has already been sent
					if isinstance(result, dict) and result.get("Type") == "error":
						msg = result["Message"]
						raise exceptions.PartialErrorResponse(msg, None, [])
					
					return result
				except StopIteration:
					self._parser_iter = None

					# Forward exception to caller if we do not expect any
					# further data
					if self._response_iter is None:
						raise

			# Iterator fuse to prevent crash after EOS/.close()
			if self._response_iter is None:
				raise StopIteration()

			try:
				data = next(self._response_iter)  # type: bytes

				# Create new parser iterator using the newly recieved data
				self._parser_iter = iter(self._parser.parse_partial(data))
			except StopIteration:
				# No more data to receive – destroy response iterator and
				# iterate over the final fragments returned by the parser
				self._response_iter = None
				self._parser_iter   = iter(self._parser.parse_finalize())
	
	def __enter__(self) -> "StreamDecodeIterator[T_co]":
		return self
	
	def __exit__(self, *a) -> None:
		self.close()
	
	def close(self) -> None:
		# Clean up any open iterators first
		if self._response_iter is not None:
			self._response_iter.close()
		if self._parser_iter is not None:
			self._parser_iter.close()
		self._response_iter = None
		self._parser_iter   = None

		# Clean up response object and parser
		if self._response is not None:
			self._response.close()
		self._response = None
		self._parser   = None

		_notify_stream_iter_closed()



if ty.TYPE_CHECKING:
	@ty.overload
	def stream_decode_full(
			response: Closable,
			response_iter: ty.Generator[bytes, ty.Any, ty.Any],
			parser: encoding.Dummy
	) -> bytes:
		...


def stream_decode_full(
		response: requests.Response,
		parser: encoding.Encoding[T_co]
) -> ty.List[T_co]:
	with StreamDecodeIterator(response, parser) as response_iter:
		# Collect all responses
		result = list(response_iter)
		
		# Return byte streams concatenated into one message, instead of split
		# at arbitrary boundaries
		if parser.is_stream:
			return b"".join(result)
		return result


class HTTPClient:
	"""An HTTP client for interacting with the IPFS daemon.

	Parameters
	----------
	addr : Union[str, multiaddr.Multiaddr]
		The address where the IPFS daemon may be reached
	base : str
		The path prefix for API calls
	workarounds : Set[str]
		List of daemon workarounds to apply
	timeout : Union[numbers.Real, Tuple[numbers.Real, numbers.Real], NoneType]
		The default number of seconds to wait when establishing a connection to
		the daemon and waiting for returned data before throwing
		:exc:`~ipfshttpclient.exceptions.TimeoutError`; if the value is a tuple
		its contents will be interpreted as the values for the connection and
		receiving phases respectively, otherwise the value will apply to both
		phases; if the value is ``None`` then all timeouts will be disabled
	defaults : dict
		The default parameters to be passed to
		:meth:`~ipfshttpclient.http.HTTPClient.request`
	"""
	
	__metaclass__ = abc.ABCMeta
	
	def __init__(self, addr, base, workarounds=None, **defaults):
		addr = multiaddr.Multiaddr(addr)
		addr_iter = iter(addr.items())
		
		# Parse the `host`, `family`, `port` & `secure` values from the given
		# multiaddr, raising on unsupported `addr` values
		try:
			# Read host value
			proto, host = next(addr_iter)
			family = socket.AF_UNSPEC
			if proto.code in (P_IP4, P_DNS4):
				family = socket.AF_INET
			elif proto.code in (P_IP6, P_DNS6):
				family = socket.AF_INET6
			elif proto.code != P_DNS:
				raise exceptions.AddressError(addr)
			
			# Read port value
			proto, port = next(addr_iter)
			if proto.code != P_TCP:
				raise exceptions.AddressError(addr)
			
			# Read application-level protocol name
			secure = False
			try:
				proto, value = next(addr_iter)
			except StopIteration:
				pass
			else:
				if proto.code == P_HTTPS:
					secure = True
				elif proto.code != P_HTTP:
					raise exceptions.AddressError(addr)
			
			# No further values may follow; this also exhausts the iterator
			was_final = all(True for _ in addr_iter)
			if not was_final:
				raise exceptions.AddressError(addr)
		except StopIteration:
			raise exceptions.AddressError(addr) from None

		# Convert the parsed `addr` values to a URL base and parameters
		# for `requests`
		if ":" in host and not host.startswith("["):
			host = "[{0}]".format(host)
		self.base = urllib.parse.SplitResult(
			scheme   = "http" if not secure else "https",
			netloc   = "{0}:{1}".format(host, port),
			path     = base,
			query    = "",
			fragment = ""
		).geturl()
		self._kwargs = {}
		if PATCH_REQUESTS:  # pragma: no branch (always enabled in production)
			self._kwargs["family"] = family
		self.defaults = defaults
		self._session = None
		
		self.workarounds = workarounds if workarounds else set()
	
	def open_session(self):
		"""Open a persistent backend session that allows reusing HTTP
		connections between individual HTTP requests.
		
		It is an error to call this function if a session is already open."""
		assert self._session is None
		self._session = requests.Session()
	
	def close_session(self):
		"""Close a session opened by
		:meth:`~ipfshttpclient.http.HTTPClient.open_session`.
		
		If there is no session currently open (ie: it was already closed), then
		this method does nothing."""
		if self._session is not None:
			self._session.close()
			self._session = None

	def _do_request(self, *args, **kwargs):
		for name, value in self._kwargs.items():
			kwargs.setdefault(name, value)
		try:
			if self._session:
				return self._session.request(*args, **kwargs)
			else:
				return requests.request(*args, **kwargs)
		except (requests.ConnectTimeout, requests.Timeout) as error:
			raise exceptions.TimeoutError(error) from error
		except requests.ConnectionError as error:
			raise exceptions.ConnectionError(error) from error
		except http.client.HTTPException as error:
			raise exceptions.ProtocolError(error) from error

	def _do_raise_for_status(self, response):
		try:
			response.raise_for_status()
		except requests.exceptions.HTTPError as error:
			content = []
			try:
				decoder = encoding.get_encoding("json")
				for chunk in response.iter_content(chunk_size=None):
					content += list(decoder.parse_partial(chunk))
				content += list(decoder.parse_finalize())
			except exceptions.DecodingError:
				pass

			# If we have decoded an error response from the server,
			# use that as the exception message; otherwise, just pass
			# the exception on to the caller.
			if len(content) == 1 \
			   and isinstance(content[0], dict) \
			   and "Message" in content[0]:
				msg = content[0]["Message"]
				raise exceptions.ErrorResponse(msg, error) from error
			else:
				raise exceptions.StatusError(error) from error
	
	def _request(
			self, url: str, params: ty.Sequence[ty.Tuple[str, str]],
			stream: bool = False,
			return_result: bool = True,
			auth: auth_t = None,
			cookies: cookies_t = None,
			data: reqdata_sync_t = None,
			headers: headers_t = {},
			timeout: timeout_t = 120,
	) -> requests.Response:
		# HTTP method must always be "POST"
		method = "POST"
		if "use_http_head_for_no_result" in self.workarounds and not return_result:
			method = "HEAD"
		
		if timeout is not None:
			if isinstance(timeout, tuple) and len(timeout) == 2:
				timeout = (
					timeout[0] if timeout[0] < math.inf else None,
					timeout[1] if timeout[1] < math.inf else None,
				)
			else:
				timeout = timeout if timeout < math.inf else None
		
		# Do HTTP request (synchronously)
		res = self._do_request(method, url, params=params, stream=stream,
		                       headers=headers, auth=auth, cookies=cookies,
		                       data=data, timeout=timeout)
		
		# Raise exception for response status
		# (optionally incorporating the response message, if applicable)
		self._do_raise_for_status(res)
		
		return res
	
	#XXX: There must be a way to make the following shorter…
	if ty.TYPE_CHECKING:
		from typing_extensions import Literal as ty_Literal
		
		@ty.overload
		def request(
				self, path: str,
				args: ty.Sequence[str] = [], *,
				opts: ty.Mapping[str, str] = {},
				decoder: str = "none",
				stream: bool = False,
				offline: bool = False,
				return_result: ty_Literal[False],
				auth: auth_t = None,
				cookies: cookies_t = None,
				data: reqdata_sync_t = None,
				headers: headers_t = {},
				timeout: timeout_t = None
		) -> None:
			...
		
		@ty.overload
		def request(
				self, path: str,
				args: ty.Sequence[str] = [], *,
				opts: ty.Mapping[str, str] = {},
				decoder: ty_Literal["none"] = "none",
				stream: ty_Literal[False] = False,
				offline: bool = False,
				return_result: ty_Literal[True] = True,
				auth: auth_t = None,
				cookies: cookies_t = None,
				data: reqdata_sync_t = None,
				headers: headers_t = {},
				timeout: timeout_t = None
		) -> bytes:
			...
		
		@ty.overload
		def request(
				self, path: str,
				args: ty.Sequence[str] = [], *,
				opts: ty.Mapping[str, str] = {},
				decoder: ty_Literal["none"] = "none",
				stream: ty_Literal[True],
				offline: bool = False,
				return_result: ty_Literal[True] = True,
				auth: auth_t = None,
				cookies: cookies_t = None,
				data: reqdata_sync_t = None,
				headers: headers_t = {},
				timeout: timeout_t = None
		) -> StreamDecodeIterator[bytes]:
			...
		
		@ty.overload
		def request(
				self, path: str,
				args: ty.Sequence[str] = [], *,
				opts: ty.Mapping[str, str] = {},
				decoder: ty_Literal["json"],
				stream: ty_Literal[False] = False,
				offline: bool = False,
				return_result: ty_Literal[True] = True,
				auth: auth_t = None,
				cookies: cookies_t = None,
				data: reqdata_sync_t = None,
				headers: headers_t = {},
				timeout: timeout_t = None
		) -> ty.List[object]:
			...
	
	@pass_defaults
	def request(
			self, path: str,
			args: ty.Sequence[str] = [], *,
			opts: ty.Mapping[str, str] = {},
			decoder: str = "none",
			stream: bool = False,
			offline: bool = False,
			return_result: bool = True,
			auth: auth_t = None,
			cookies: cookies_t = None,
			data: reqdata_sync_t = None,
			headers: headers_t = {},
			timeout: timeout_t = None
	) -> ty.Optional[ty.Union[  # noqa: ET122 (false positive)
		StreamDecodeIterator[bytes],
		StreamDecodeIterator[object],
		bytes,
		ty.List[object],
	]]:
		"""Makes an HTTP request to the IPFS daemon.

		This function returns the contents of the HTTP response from the IPFS
		daemon.

		Raises
		------
		~ipfshttpclient.exceptions.ErrorResponse
		~ipfshttpclient.exceptions.ConnectionError
		~ipfshttpclient.exceptions.ProtocolError
		~ipfshttpclient.exceptions.StatusError
		~ipfshttpclient.exceptions.TimeoutError

		Parameters
		----------
		path
			The command path relative to the given base
		decoder
			The encoder to use to parse the HTTP response
		stream
			Whether to return an iterable yielding the received items incrementally
			instead of receiving and decoding all items up-front before returning
			them
		args
			Positional parameters to be sent along with the HTTP request
		opts
			Query string paramters to be sent along with the HTTP request
		offline
			Whether to request to daemon to handle this request in “offline-mode”
		return_result
			Whether to decode the values received from the daemon
		auth
			Authentication data to send along with this request as
			``(username, password)`` tuple
		cookies
			HTTP cookies to send along with each request to the API daemon
		data
			Iterable yielding data to stream from the client to the daemon
		headers
			Custom HTTP headers to pass send along with the request
		timeout
			How many seconds to wait for the server to send data
			before giving up
			
			Set this to :py:`math.inf` to disable timeouts entirely.
		"""
		url = self.base + path

		params = []
		params.append(('stream-channels', 'true'))
		if offline:
			params.append(('offline', 'true'))
		for opt in opts.items():
			params.append(opt)
		for arg in args:
			params.append(('arg', arg))
		
		# Don't attempt to decode response or stream
		# (which would keep an iterator open that will then never be waited for)
		if not return_result:
			decoder = None
			stream = False

		parser = encoding.get_encoding(decoder if decoder else "none")
		
		res = self._request(url, params, stream, return_result,
		                    auth, cookies, data, headers, timeout)
		
		if not return_result:
			return None
		elif stream:
			# Decode each item as it is read
			return StreamDecodeIterator(res, parser)
		else:
			# Decode received item immediately
			return stream_decode_full(res, parser)

	@pass_defaults
	def download(
			self, path: str,
			args: ty.Sequence[str] = [], *,
			filepath: ty.Optional[str] = None,
			opts: ty.Mapping[str, str] = {},
			compress: bool = False,
			offline: bool = False,
			auth: auth_t = None,
			cookies: cookies_t = None,
			headers: headers_t = {},
			timeout: timeout_t = 120
	) -> None:
		"""Makes a request to the IPFS daemon to download a file.

		Downloads a file or files from IPFS into the current working
		directory, or the directory given by ``filepath``.

		Raises
		------
		~ipfshttpclient.exceptions.ErrorResponse
		~ipfshttpclient.exceptions.ConnectionError
		~ipfshttpclient.exceptions.ProtocolError
		~ipfshttpclient.exceptions.StatusError
		~ipfshttpclient.exceptions.TimeoutError

		Parameters
		----------
		path
			The command path relative to the given base
		args
			Positional parameters to be sent along with the HTTP request
		filepath
			The local path where IPFS will store downloaded files
			
			Defaults to the current working directory.
		opts
			Query string paramters to be sent along with the HTTP request
		compress
			Whether the downloaded file should be GZip compressed by the
			daemon before being sent to the client
			
			This may greatly speed up things if data is sent across slower networks
			like the internet but is a major bottleneck when communicating with the
			daemon on ``localhost``.
		offline
			Whether to request to daemon to handle this request in “offline-mode”
		return_result
			Whether to decode the values received from the daemon
		auth
			Authentication data to send along with this request as
			``(username, password)`` tuple
		cookies
			HTTP cookies to send along with each request to the API daemon
		headers
			Custom HTTP headers to pass send along with the request
		timeout
			How many seconds to wait for the server to send data
			before giving up
			
			Set this to :py:`math.inf` to disable timeouts entirely.
		"""
		url = self.base + path
		wd = filepath or '.'

		params = []
		params.append(('stream-channels', 'true'))
		if offline:
			params.append(('offline', 'true'))
		params.append(('archive', 'true'))
		if compress:
			params.append(('compress', 'true'))
		
		for opt in opts.items():
			params.append(opt)
		for arg in args:
			params.append(('arg', arg))
		
		res = self._request(url, params, stream=True, headers=headers,
		                    auth=auth, cookies=cookies, timeout=timeout)
		
		# try to stream download as a tar file stream
		mode = 'r|gz' if compress else 'r|'
		
		with tarfile.open(fileobj=res.raw, mode=mode) as tf:
			tf.extractall(path=wd)
