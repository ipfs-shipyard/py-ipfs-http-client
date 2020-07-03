"""HTTP client for API requests based on HTTPx

This will be supplemented by an asynchronous version based on HTTPx's
asynchronous API soon™.
"""

import math
import socket
import typing as ty
import warnings

import httpx

from . import encoding
from . import exceptions
from .http_common import (
	ClientSyncBase, multiaddr_to_url_data,
	
	addr_t, auth_t, cookies_t, headers_t, params_t, reqdata_sync_t, timeout_t,
	Closable,
)


def map_args_to_httpx(
		*,
		auth: auth_t = None,
		data: reqdata_sync_t = None,
		cookies: cookies_t = None,
		headers: headers_t = None,
		params: params_t = None,
		timeout: timeout_t = None,
) -> ty.Dict[str, ty.Any]:
	kwargs: ty.Dict[str, ty.Any] = {}
	
	if auth is not None:
		kwargs["auth"] = auth
	
	if data is not None:
		kwargs["data"] = data
	
	if cookies is not None:
		kwargs["cookies"] = cookies
	
	if headers is not None:
		kwargs["headers"] = headers
	
	if timeout is not None:
		if isinstance(timeout, tuple) and len(timeout) == 2:
			timeout = (
				timeout[0] if timeout[0] < math.inf else None,
				timeout[1] if timeout[1] < math.inf else None,
			)
		else:
			timeout = timeout if timeout < math.inf else None
		kwargs["timeout"] = timeout
	
	if params is not None:
		kwargs["params"] = params
	
	return kwargs


class ClientSync(ClientSyncBase[httpx.Client]):
	__slots__ = ("_session_kwargs",)
	_session_kwargs: ty.Dict[str, ty.Any]
	
	def _init(self, addr: addr_t, base: str, *,
	          auth: auth_t,
	          cookies: cookies_t,
	          headers: headers_t,
	          params: params_t,
	          timeout: timeout_t):
		base_url: str
		family: socket.AddressFamily
		host_numeric: bool
		base_url, family, host_numeric = multiaddr_to_url_data(addr, base)
		
		#FIXME once https://github.com/encode/httpcore/pull/100 is released
		if family != socket.AF_UNSPEC and not host_numeric:
			warnings.warn(
				"Restricting the address family on name lookups is not yet supported by HTTPx",
				UserWarning
			)
		
		self._session_kwargs = map_args_to_httpx(
			auth=auth,
			cookies=cookies,
			headers=headers,
			params=params,
			timeout=timeout,
		)
		self._session_kwargs["base_url"] = base_url
	
	def _make_session(self) -> httpx.Client:
		return httpx.Client(**self._session_kwargs)
	
	def _do_raise_for_status(self, response):
		try:
			response.raise_for_status()
		except httpx.HTTPError as error:
			content: ty.List[object] = []
			try:
				decoder: encoding.Json = encoding.get_encoding("json")
				for chunk in response.iter_bytes():
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
				msg: str = content[0]["Message"]
				raise exceptions.ErrorResponse(msg, error) from error
			else:
				raise exceptions.StatusError(error) from error
	
	def _request(
			self, method: str, path: str, params: ty.Sequence[ty.Tuple[str, str]], *,
			auth: auth_t,
			data: reqdata_sync_t,
			headers: headers_t,
			timeout: timeout_t,
			chunk_size: ty.Optional[int],
	) -> ty.Tuple[ty.List[Closable], ty.Iterator[bytes]]:
		# Ensure path is relative so that it is resolved relative to the base
		while path.startswith("/"):
			path = path[1:]
		
		try:
			# Determine session object to use
			closables: ty.List[Closable]
			session: httpx.Client
			closables, session = self._access_session()
			
			# Do HTTP request (synchronously) and map exceptions
			try:
				res: httpx.Response = session.stream(
					method=method,
					url=path,
					**map_args_to_httpx(
						params=params,
						auth=auth,
						data=data,
						headers=headers,
						timeout=timeout,
					)
				).__enter__()
				closables.insert(0, res)
			except (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.WriteTimeout) as error:
				raise exceptions.TimeoutError(error) from error
			except httpx.NetworkError as error:
				raise exceptions.ConnectionError(error) from error
			except httpx.ProtocolError as error:
				raise exceptions.ProtocolError(error) from error
			
			# Raise exception for response status
			# (optionally incorporating the response message, if available)
			self._do_raise_for_status(res)
			
			return closables, res.iter_bytes()
		except:
			for closable in closables:
				closable.close()
			raise