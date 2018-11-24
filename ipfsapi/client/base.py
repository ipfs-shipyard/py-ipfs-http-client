# -*- coding: utf-8 -*-
from __future__ import absolute_import

import warnings

import ipfsapi.http
import ipfsapi.multipart

from . import DEFAULT_HOST, DEFAULT_PORT, DEFAULT_BASE


class SectionProperty(object):
	def __init__(self, cls):
		self.cls      = cls
		self.instance = None

	def __get__(self, client_object, type=None):
		if not self.instance:
			self.instance = self.cls(client_object)

		return self.instance


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
	"""A TCP client for interacting with an IPFS daemon.

	A :class:`~ipfsapi.Client` instance will not actually establish a
	connection to the daemon until at least one of it's methods is called.

	Parameters
	----------
	host : str
		Hostname or IP address of the computer running the ``ipfs daemon``
		node (defaults to the local system)
	port : int
		The API port of the IPFS deamon (usually 5001)
	base : str
		Path of the deamon's API (currently always ``api/v0``)
	chunk_size : int
		The size of the chunks to break uploaded files and text content into
	"""

	_clientfactory = ipfsapi.http.HTTPClient

	def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT,
	             base=DEFAULT_BASE, chunk_size=ipfsapi.multipart.default_chunk_size,
	             **defaults):
		"""Connects to the API port of an IPFS node."""

		self.chunk_size = chunk_size

		self._client = self._clientfactory(host, port, base, **defaults)


class DeprecatedMethodProperty(object):
	def __init__(self, *path, **kwargs):
		#PY2: No support for kw-only parameters after glob parameters
		prefix = kwargs.pop("prefix", [])
		strip  = kwargs.pop("strip", 0)
		assert not kwargs

		self.props  = path
		self.path   = tuple(prefix) + (path[:-strip] if strip > 0 else tuple(path))
		self.warned = False

		self.__help__ = "Deprecated method: Please use “client.{0}” instead".format(
			".".join(self.path)
		)

	def __get__(self, obj, type=None):
		if not self.warned:
			message = "IPFS API function “{0}” has been renamed to “{1}”".format(
				"_".join(self.path), ".".join(self.path)
			)
			warnings.warn(message, FutureWarning)
			self.warned = True
		print()
		for name in self.props:
			print(name, obj)
			obj = getattr(obj, name)
		return obj
