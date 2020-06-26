import collections.abc
import functools
import typing as ty

from . import DEFAULT_ADDR, DEFAULT_BASE

from .. import multipart, http


json_value_t = ty.Union[bool, float, int, str,
                        ty.List["json_value_t"],
                        ty.Dict[str, "json_value_t"]]


class ResponseBase(collections.abc.Mapping):
	"""Base class for wrapping IPFS node API responses
	
	Original JSON properties are exposed using dict item syntax ``response[key]``.
	To access the raw parsed JSON object use the :meth:`as_json` method.
	"""
	__slots__ = ("_raw",)
	#_raw: ty.Dict[str, json_value_t]
	
	_repr_attr_display = list()  # type: ty.Sequence[str]
	_repr_json_hidden  = set()  # type: ty.Container[str]
	
	def __init__(self, response: ty.Dict[str, json_value_t]):
		self._raw = dict(response)
	
	def __getitem__(self, name: str) -> ty.Union[bool, float, int, str, "ResponseBase"]:
		return self._wrap_result(self._raw[name])
	
	@classmethod
	def _wrap_result(cls, value: json_value_t) \
	    -> ty.Union[bool, float, int, str, "ResponseBase"]:
		if isinstance(value, dict):
			value = ResponseBase(value)
		elif isinstance(value, list):
			value = [cls._wrap_result(v) for v in value]
		return value
	
	def __iter__(self) -> ty.Iterator[str]:
		return iter(self._raw)
	
	def __len__(self) -> int:
		return len(self._raw)
	
	def __repr__(self) -> str:
		attr_str_parts = []  # type: ty.List[str]
		for name in type(self)._repr_attr_display:
			attr_str_parts.append("{0}={1!r}".format(name, getattr(self, name)))
		
		json_hidden = type(self)._repr_json_hidden
		attr_json_parts = []  # type: ty.List[str]
		for name, value in filter(lambda i: i[0] not in json_hidden, self._raw.items()):
			attr_json_parts.append("{0!r}: {1!r}".format(name, value))
		
		#arg_str: str
		if attr_str_parts and attr_json_parts:
			arg_str = "{0}, **{{{1}}}".format(", ".join(attr_str_parts), ", ".join(attr_json_parts))
		elif attr_str_parts:
			arg_str = ", ".join(attr_str_parts)
		else:
			arg_str = "{{{0}}}".format(", ".join(attr_json_parts))
		
		return "<{0.__module__}.{0.__qualname__}: {1}>".format(type(self), arg_str)
	
	def as_json(self) -> ty.Dict[str, json_value_t]:
		"""Returns the original parsed JSON object as returned by the remote IPFS node
		
		In general, try to avoid modifying the returned dictionary if plan on
		subsequently using this response object.
		"""
		return self._raw


T = ty.TypeVar("T")
R = ty.TypeVar("R")

wrap_cb_t = ty.Callable[[T], R]


def ident(value: T) -> T:
	return value


class ResponseWrapIterator(ty.Generic[T, R]):
	__slots__ = ("_inner", "_item_wrap_cb")
	#_inner: http.StreamDecodeIteratorSync
	#_item_wrap_cb: wrap_cb_t
	
	def __init__(self, inner: http.StreamDecodeIteratorSync, item_wrap_cb: wrap_cb_t):
		self._inner = inner
		self._item_wrap_cb = item_wrap_cb
	
	def __iter__(self) -> "ResponseWrapIterator[T, R]":
		return self
	
	def __next__(self) -> R:
		return self._item_wrap_cb(next(self._inner))
	
	def __enter__(self) -> "ResponseWrapIterator[T, R]":
		self._inner.__enter__()
		return self
	
	def __exit__(self, *args) -> None:
		self._inner.__exit__(*args)
	
	def close(self) -> None:
		self._inner.close()


def returns_multiple_items(item_wrap_cb: wrap_cb_t = ident, *, stream: bool = False):
	def wrapper1(func: ty.Callable[..., T]):
		@functools.wraps(func)
		def wrapper2(*args: ty.Any, **kwargs: ty.Any) -> R:
			result = func(*args, **kwargs)  # type: T
			if isinstance(result, list):
				return [item_wrap_cb(r) for r in result]
			if result is None:
				assert not kwargs.get("return_result", True)
				return None
			assert kwargs.get("stream", False) or stream, (
				"Called IPFS HTTP-Client function should only ever return a list, "
				"when not streaming a response"
			)
			return ResponseWrapIterator(result, item_wrap_cb)
		return wrapper2
	return wrapper1


def returns_single_item(item_wrap_cb: wrap_cb_t = ident, *, stream: bool = False):
	def wrapper1(func: ty.Callable[..., T]):
		@functools.wraps(func)
		def wrapper2(*args: ty.Any, **kwargs: ty.Any) -> R:
			result = func(*args, **kwargs)  # type: T
			if isinstance(result, list):
				assert len(result) == 1, ("Called IPFS HTTP-Client function should "
				                          "only ever return one item")
				return item_wrap_cb(result[0])
			if result is None:
				assert not kwargs.get("return_result", True)
				return None
			assert kwargs.get("stream", False) or stream, (
				"Called IPFS HTTP-Client function should only ever return a list "
				"with a single item, when not streaming a response"
			)
			return ResponseWrapIterator(result, item_wrap_cb)
		return wrapper2
	return wrapper1


def returns_no_item(func):
	@functools.wraps(func)
	def wrapper(*args, **kwargs):
		result = func(*args, **kwargs)
		if isinstance(result, (list, bytes, object)):
			assert not result, ("Called IPFS HTTP-Client function should never "
			                    "return a non-empty item")
			return
		assert kwargs.get("stream", False), ("Called IPFS HTTP-Client function "
		                                     "should only ever return an empty "
		                                     "object, when not  streaming a "
		                                     "response")
		return result
	return wrapper


class SectionProperty:
	def __init__(self, cls):
		self.__prop_cls__ = cls

	def __get__(self, client_object, type=None):
		if client_object is not None:  # We are invoked on object
			try:
				return client_object.__prop_objs__[self]
			except AttributeError:
				client_object.__prop_objs__ = {
					self: self.__prop_cls__(client_object)
				}
				return client_object.__prop_objs__[self]
			except KeyError:
				client_object.__prop_objs__[self] = self.__prop_cls__(client_object)
				return client_object.__prop_objs__[self]
		else:  # We are invoked on class
			return self.__prop_cls__


class SectionBase:
	# Accept parent object from property descriptor
	def __init__(self, parent):
		self.__parent = parent

	# Proxy the parent's properties
	@property
	def _client(self):
		return self.__parent._client

	@property
	def chunk_size(self):
		return self.__parent.chunk_size

	@chunk_size.setter
	def chunk_size(self, value):
		self.__parent.chunk_size = value


class ClientBase:
	"""
	Parameters
	----------
	addr
		The `Multiaddr <dweb:/ipns/multiformats.io/multiaddr/>`_ describing the
		API daemon location, as used in the *API* key of `go-ipfs Addresses
		section
		<https://github.com/ipfs/go-ipfs/blob/master/docs/config.md#addresses>`_
		
		Supported addressing patterns are currently:
		
		 * ``/{dns,dns4,dns6,ip4,ip6}/<host>/tcp/<port>`` (HTTP)
		 * ``/{dns,dns4,dns6,ip4,ip6}/<host>/tcp/<port>/http`` (HTTP)
		 * ``/{dns,dns4,dns6,ip4,ip6}/<host>/tcp/<port>/https`` (HTTPS)
		
		Additional forms (proxying) may be supported in the future.
	base
		The HTTP URL path prefix (or “base”) at which the API is exposed on the
		API daemon
	chunk_size
		The size of data chunks passed to the operating system when uploading
		files or text/binary content
	offline
		Ask daemon to operate in “offline mode” – that is, it should not consult
		the network when unable to find resources locally, but fail instead
	session
		Create this :class:`~ipfshttpclient.Client` instance with a session
		already open? (Useful for long-running client objects.)
	auth
		HTTP basic authentication `(username, password)` tuple to send along with
		each request to the API daemon
	cookies
		HTTP cookies to send along with each request to the API daemon
	headers
		Custom HTTP headers to send along with each request to the API daemon
	timeout
		Connection timeout (in seconds) when connecting to the API daemon
		
		If a tuple is passed its contents will be interpreted as the values for
		the connecting and receiving phases respectively, otherwise the value will
		apply to both phases.
		
		The default value is implementation-defined. A value of `math.inf`
		disables the respective timeout.
	"""
	
	def __init__(
			self,
			addr: http.addr_t = DEFAULT_ADDR,
			base: str = DEFAULT_BASE, *,
			
			chunk_size: int = multipart.default_chunk_size,
			offline: bool = False,
			session: bool = False,
			
			auth: http.auth_t = None,
			cookies: http.cookies_t = None,
			headers: http.headers_t = {},
			timeout: http.timeout_t = 120,
			
			# Backward-compat
			username: ty.Optional[str] = None,
			password: ty.Optional[str] = None
	):
		"""Connects to the API port of an IPFS node."""
		
		self.chunk_size = chunk_size
		
		if auth is None and (username or password):
			auth = (username, password)
		
		self._client = http.ClientSync(
			addr, base, offline=offline,
			auth=auth, cookies=cookies, headers=headers, timeout=timeout,
		)
		if session:
			self._client.open_session()
		
		self._workarounds = self._client.workarounds
