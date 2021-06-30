"""HTTP client for API requests based on good old requests library

This exists mainly for Python 3.5 compatibility.
"""

import math
import http.client
import requests
import typing as ty
import urllib.parse

import urllib3.exceptions  # type: ignore[import]

from . import encoding
from . import exceptions
from .http_common import (
	ClientSyncBase, multiaddr_to_url_data,
	
	addr_t, auth_t, cookies_t, headers_t, params_t, reqdata_sync_t, timeout_t,
	Closable,
)
from .requests_wrapper import PATCH_REQUESTS
from .requests_wrapper import wrapped_session


def map_args_to_requests(
		*,
		auth: auth_t = None,
		cookies: cookies_t = None,
		headers: headers_t = None,
		params: params_t = None,
		timeout: timeout_t = None
) -> ty.Dict[str, ty.Any]:
	kwargs = {}  # type: ty.Dict[str, ty.Any]
	
	if auth is not None:
		kwargs["auth"] = auth
	
	if cookies is not None:
		kwargs["cookies"] = cookies
	
	if headers is not None:
		kwargs["headers"] = headers
	
	if timeout is not None:
		if isinstance(timeout, tuple):
			timeout_ = (
				timeout[0] if timeout[0] < math.inf else None,
				timeout[1] if timeout[1] < math.inf else None,
			)  # type: ty.Union[ty.Optional[float], ty.Tuple[ty.Optional[float], ty.Optional[float]]]
		else:
			timeout_ = timeout if timeout < math.inf else None
		kwargs["timeout"] = timeout_
	
	if params is not None:
		kwargs["params"] = {}
		for name, value in params:
			if name not in kwargs["params"]:
				kwargs["params"][name] = value
			elif not isinstance(kwargs["params"][name], list):
				kwargs["params"][name] = [kwargs["params"][name], value]
			else:
				kwargs["params"][name].append(value)
	
	return kwargs


class ClientSync(ClientSyncBase[requests.Session]):
	__slots__ = ("_base_url", "_default_timeout", "_request_proxies", "_session_props")
	#_base_url: str
	#_default_timeout: timeout_t
	#_request_proxies: ty.Optional[ty.Dict[str, str]]
	#_session_props: ty.Dict[str, ty.Any]
	
	def _init(self, addr: addr_t, base: str, *,  # type: ignore[no-any-unimported]
	          auth: auth_t,
	          cookies: cookies_t,
	          headers: headers_t,
	          params: params_t,
	          timeout: timeout_t) -> None:
		self._base_url, uds_path, family, host_numeric = multiaddr_to_url_data(addr, base)
		
		self._session_props = map_args_to_requests(
			auth=auth,
			cookies=cookies,
			headers=headers,
			params=params,
		)
		self._default_timeout = timeout

		if PATCH_REQUESTS:
			self._session_props["family"] = family
		
		# Ensure that no proxy lookups are done for the UDS pseudo-hostname
		#
		# I'm well aware of the `.proxies` attribute of the session object: As it turns out,
		# setting *that* attribute will *not* bypass system proxy resolution – only the
		# per-request keyword-argument can do *that*…!
		self._request_proxies = None  # type: ty.Optional[ty.Dict[str, str]]
		if uds_path:
			self._request_proxies = {
				"no_proxy": urllib.parse.quote(uds_path, safe=""),
			}
	
	def _make_session(self) -> requests.Session:
		session = wrapped_session()
		try:
			for name, value in self._session_props.items():
				setattr(session, name, value)
			return session
		# It is very unlikely that this would ever error, but if it does try our
		# best to prevent a leak
		except:  # pragma: no cover
			session.close()
			raise
	
	def _do_raise_for_status(self, response: requests.Response) -> None:
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
			self, method: str, path: str, params: ty.Sequence[ty.Tuple[str, str]], *,
			auth: auth_t,
			data: reqdata_sync_t,
			headers: headers_t,
			timeout: timeout_t,
			chunk_size: ty.Optional[int]
	) -> ty.Tuple[ty.List[Closable], ty.Generator[bytes, ty.Any, ty.Any]]:
		# Ensure path is relative so that it is resolved relative to the base
		while path.startswith("/"):
			path = path[1:]
		
		url = urllib.parse.urljoin(self._base_url, path)

		try:
			# Determine session object to use
			closables, session = self._access_session()
			
			# Do HTTP request (synchronously) and map exceptions
			try:
				res = session.request(
					method=method,
					url=url,
					**map_args_to_requests(
						params=params,
						auth=auth,
						headers=headers,
						timeout=(timeout if timeout is not None else self._default_timeout),
					),
					proxies=self._request_proxies,
					# requests.Session.request does not accept Optional[Iterator[bytes]],
					# but we seem to be passing that here.
					data=data,  # type: ignore[arg-type]
					stream=True,
				)
				closables.insert(0, res)
			except (requests.ConnectTimeout, requests.Timeout) as error:  # type: ignore[attr-defined]
				raise exceptions.TimeoutError(error) from error
			except requests.ConnectionError as error:
				# Report protocol violations separately
				#
				# This used to happen because requests wouldn't catch
				# `http.client.HTTPException` at all, now we recreate
				# this behaviour manually if we detect it.
				if isinstance(error.args[0], urllib3.exceptions.ProtocolError):
					raise exceptions.ProtocolError(error.args[0]) from error.args[0]
				
				raise exceptions.ConnectionError(error) from error
			# Looks like the following error doesn't happen anymore with modern requests?
			except http.client.HTTPException as error:  # pragma: no cover
				raise exceptions.ProtocolError(error) from error
			
			# Raise exception for response status
			# (optionally incorporating the response message, if available)
			self._do_raise_for_status(res)
			
			return closables, (portion for portion in res.iter_content(chunk_size=chunk_size))
		except:
			for closable in closables:
				closable.close()
			raise
