# -*- coding: utf-8 -*-
from __future__ import absolute_import
import functools

import six

from . import DEFAULT_ADDR, DEFAULT_BASE

from .. import multipart, http


def returns_single_item(func):
	@functools.wraps(func)
	def wrapper(*args, **kwargs):
		result = func(*args, **kwargs)
		if isinstance(result, list):
			if len(result) != 1:
				print(result)
			assert len(result) == 1, ("Called IPFS HTTP-Client function should "
			                          "only ever return one item")
			return result[0]
		assert kwargs.get("stream", False), ("Called IPFS HTTP-Client function "
		                                     "should only ever return a list, "
		                                     "when not streaming a response")
		return result
	return wrapper


def returns_no_item(func):
	@functools.wraps(func)
	def wrapper(*args, **kwargs):
		result = func(*args, **kwargs)
		if isinstance(result, (list, six.binary_type)):
			assert len(result) == 0, ("Called IPFS HTTP-Client function should "
			                          "never return an item")
			return
		assert kwargs.get("stream", False), ("Called IPFS HTTP-Client function "
		                                     "should only ever return a list "
		                                     "or bytes, when not streaming a "
		                                     "response")
		return result
	return wrapper


class SectionProperty(object):
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


class SectionBase(object):
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


class ClientBase(object):
	"""
	Parameters
	----------
	addr : Union[bytes, str, multiaddr.Multiaddr]
		The `MultiAddr <dweb:/ipns/multiformats.io/multiaddr/>`_ describing the
		API daemon location, as used in the *API* key of `go-ipfs Addresses
		section
		<https://github.com/ipfs/go-ipfs/blob/master/docs/config.md#addresses>`_
		
		Supported addressing patterns are currently:
		 
		 * ``/{dns,dns4,dns6,ip4,ip6}/<host>/tcp/<port>`` (HTTP)
		 * ``/{dns,dns4,dns6,ip4,ip6}/<host>/tcp/<port>/http`` (HTTP)
		 * ``/{dns,dns4,dns6,ip4,ip6}/<host>/tcp/<port>/https`` (HTTPS)
		
		Additional forms (proxying) may be supported in the future.
	base : str
		The HTTP URL path prefix (or “base”) at which the API is exposed on the
		API daemon
	chunk_size : int
		The size of the chunks to break uploaded files and text content into
	"""

	_clientfactory = http.HTTPClient

	def __init__(self, addr=DEFAULT_ADDR, base=DEFAULT_BASE,
	             chunk_size=multipart.default_chunk_size,
	             **defaults):
		"""Connects to the API port of an IPFS node."""

		self.chunk_size = chunk_size

		self._client = self._clientfactory(addr, base, **defaults)