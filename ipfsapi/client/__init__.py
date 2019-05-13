# -*- coding: utf-8 -*-
"""IPFS API Bindings for Python.

Classes:

 * Client – a TCP client for interacting with an IPFS daemon
"""
from __future__ import absolute_import

import functools
import inspect
import os
import re
import warnings
try:  #PY3
	import urllib.parse
except ImportError:  #PY2
	class urllib:
		import urlparse as parse

import ipfshttpclient
import netaddr

DEFAULT_HOST = str(os.environ.get("PY_IPFSAPI_DEFAULT_HOST", 'localhost'))
DEFAULT_PORT = int(os.environ.get("PY_IPFSAPI_DEFAULT_PORT", 5001))
DEFAULT_BASE = str(os.environ.get("PY_IPFSAPI_DEFAULT_BASE", 'api/v0'))

VERSION_MINIMUM = "0.4.3"
VERSION_MAXIMUM = "0.5.0"

from .. import exceptions, encoding

from . import base


def assert_version(version, minimum=VERSION_MINIMUM, maximum=VERSION_MAXIMUM):
	"""Make sure that the given daemon version is supported by this client
	version.

	Raises
	------
	~ipfsapi.exceptions.VersionMismatch

	Parameters
	----------
	version : str
		The version of an IPFS daemon.
	minimum : str
		The minimal IPFS version to allow.
	maximum : str
		The maximum IPFS version to allow.
	"""
	# Convert version strings to integer tuples
	version = list(map(int, version.split('-', 1)[0].split('.')))
	minimum = list(map(int, minimum.split('-', 1)[0].split('.')))
	maximum = list(map(int, maximum.split('-', 1)[0].split('.')))

	if minimum > version or version >= maximum:
		raise exceptions.VersionMismatch(version, minimum, maximum)


def connect(host=DEFAULT_HOST, port=DEFAULT_PORT, base=DEFAULT_BASE,
            chunk_size=4096, **defaults):
	"""Create a new :class:`~ipfsapi.Client` instance and connect to the
	daemon to validate that its version is supported.

	Raises
	------
	~ipfsapi.exceptions.VersionMismatch
	~ipfsapi.exceptions.ErrorResponse
	~ipfsapi.exceptions.ConnectionError
	~ipfsapi.exceptions.ProtocolError
	~ipfsapi.exceptions.StatusError
	~ipfsapi.exceptions.TimeoutError


	All parameters are identical to those passed to the constructor of the
	:class:`~ipfsapi.Client` class.

	Returns
	-------
		~ipfsapi.Client
	"""
	# Create client instance
	client = Client(host, port, base, chunk_size, **defaults)

	# Query version number from daemon and validate it
	assert_version(client.version()['Version'])

	return client


class Client(ipfshttpclient.Client):
	# Aliases for previous method names
	key_gen    = base.DeprecatedMethodProperty("key", "gen")
	key_list   = base.DeprecatedMethodProperty("key", "list")
	key_rename = base.DeprecatedMethodProperty("key", "rename")
	key_rm     = base.DeprecatedMethodProperty("key", "rm")

	block_get  = base.DeprecatedMethodProperty("block", "get")
	block_put  = base.DeprecatedMethodProperty("block", "put")
	block_stat = base.DeprecatedMethodProperty("block", "stat")

	files_cp    = base.DeprecatedMethodProperty("files", "cp")
	files_ls    = base.DeprecatedMethodProperty("files", "ls")
	files_mkdir = base.DeprecatedMethodProperty("files", "mkdir")
	files_stat  = base.DeprecatedMethodProperty("files", "stat")
	files_rm    = base.DeprecatedMethodProperty("files", "rm")
	files_read  = base.DeprecatedMethodProperty("files", "read")
	files_write = base.DeprecatedMethodProperty("files", "write")
	files_mv    = base.DeprecatedMethodProperty("files", "mv")

	object_data  = base.DeprecatedMethodProperty("object", "data")
	object_get   = base.DeprecatedMethodProperty("object", "get")
	object_links = base.DeprecatedMethodProperty("object", "links")
	object_new   = base.DeprecatedMethodProperty("object", "new")
	object_put   = base.DeprecatedMethodProperty("object", "put")
	object_stat  = base.DeprecatedMethodProperty("object", "stat")
	object_patch_add_link    = base.DeprecatedMethodProperty("object", "patch", "add_link")
	object_patch_append_data = base.DeprecatedMethodProperty("object", "patch", "append_data")
	object_patch_rm_link     = base.DeprecatedMethodProperty("object", "patch", "rm_link")
	object_patch_set_data    = base.DeprecatedMethodProperty("object", "patch", "set_data")

	pin_add    = base.DeprecatedMethodProperty("pin", "add")
	pin_ls     = base.DeprecatedMethodProperty("pin", "ls")
	pin_rm     = base.DeprecatedMethodProperty("pin", "rm")
	pin_update = base.DeprecatedMethodProperty("pin", "update")
	pin_verify = base.DeprecatedMethodProperty("pin", "verify")

	refs       = base.DeprecatedMethodProperty("unstable", "refs")
	refs_local = base.DeprecatedMethodProperty("unstable", "refs", "local")

	bootstrap_add  = base.DeprecatedMethodProperty("bootstrap", "add")
	bootstrap_list = base.DeprecatedMethodProperty("bootstrap", "list")
	bootstrap_rm   = base.DeprecatedMethodProperty("bootstrap", "rm")

	bitswap_stat     = base.DeprecatedMethodProperty("bitswap", "stat")
	bitswap_wantlist = base.DeprecatedMethodProperty("bitswap", "wantlist")

	dht_findpeer  = base.DeprecatedMethodProperty("dht", "findpeer")
	dht_findprovs = base.DeprecatedMethodProperty("dht", "findproves")
	dht_get       = base.DeprecatedMethodProperty("dht", "get")
	dht_put       = base.DeprecatedMethodProperty("dht", "put")
	dht_query     = base.DeprecatedMethodProperty("dht", "query")

	pubsub_ls    = base.DeprecatedMethodProperty("pubsub", "ls")
	pubsub_peers = base.DeprecatedMethodProperty("pubsub", "peers")
	pubsub_pub   = base.DeprecatedMethodProperty("pubsub", "publish")
	pubsub_sub   = base.DeprecatedMethodProperty("pubsub", "subscribe")

	swarm_addrs      = base.DeprecatedMethodProperty("swarm", "addrs")
	swarm_connect    = base.DeprecatedMethodProperty("swarm", "connect")
	swarm_disconnect = base.DeprecatedMethodProperty("swarm", "disconnect")
	swarm_peers      = base.DeprecatedMethodProperty("swarm", "peers")
	swarm_filters_add = base.DeprecatedMethodProperty("swarm", "filters", "add")
	swarm_filters_rm  = base.DeprecatedMethodProperty("swarm", "filters", "rm")

	name_publish = base.DeprecatedMethodProperty("name", "publish")
	name_resolve = base.DeprecatedMethodProperty("name", "resolve")

	repo_gc   = base.DeprecatedMethodProperty("repo", "gc")
	repo_stat = base.DeprecatedMethodProperty("repo", "stat")

	config         = base.DeprecatedMethodProperty("config", "set")
	config_show    = base.DeprecatedMethodProperty("config", "get")
	config_replace = base.DeprecatedMethodProperty("config", "replace")

	log_level = base.DeprecatedMethodProperty("unstable", "log", "level")
	log_ls    = base.DeprecatedMethodProperty("unstable", "log", "ls")
	log_tail  = base.DeprecatedMethodProperty("unstable", "log", "tail")

	shutdown = base.DeprecatedMethodProperty("stop")
	
	
	def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT, base=DEFAULT_BASE,
	             chunk_size=4096, **defaults):
		# Assemble and parse the URL these parameters are supposed to represent
		if not re.match('^https?://', host.lower()):
			host = 'http://' + host
		url = urllib.parse.urlsplit('%s:%s/%s' % (host, port, base))
		
		# Detect whether `host` is a (DNS) hostname or an IP address
		host_type = "dns"
		try:
			host_type = "ip{0}".format(netaddr.IPAddress(url.hostname).version)
		except netaddr.AddrFormatError:
			pass
		
		addr = "/{0}/{1}/tcp/{2}/{3}".format(host_type, url.hostname, url.port, url.scheme)
		super(Client, self).__init__(addr, base, chunk_size, timeout=None, **defaults)


	def __getattribute__(self, name):
		value = super(Client, self).__getattribute__(name)
		if inspect.ismethod(value):
			@functools.wraps(value)
			def wrapper(*args, **kwargs):
				# Rewrite changed named parameter names
				if "multihash" in kwargs:
					kwargs["cid"] = kwargs.pop("multihash")
				if "multihashes" in kwargs:
					kwargs["cids"] = kwargs.pop("multihashes")
				
				try:
					return value(*args, **kwargs)
				# Partial error responses used to incorrectly just return
				# the parts that were successfully received followed by the
				# (undetected) error frame
				except exceptions.PartialErrorResponse as error:
					return error.partial + [{"Type": "error", "Message": str(error)}]
			return wrapper
		return value


	def add(self, files, recursive=False, pattern='**', *args, **kwargs):
		# Signature changed to: add(self, *files, recursive=False, pattern='**', **kwargs)
		if not isinstance(files, (list, tuple)):
			files = (files,)
		return super(Client, self).add(*files, recursive=recursive, pattern=pattern, **kwargs)


	# Dropped API methods
	def bitswap_unwant(self, key, **kwargs):
		"""Deprecated method: Do not use anymore"""
		warnings.warn(
			"IPFS API function “bitswap_unwant” support has been dropped "
			"from go-ipfs", FutureWarning
		)
		
		args = (key,)
		return self._client.request('/bitswap/unwant', args, **kwargs)
	
	
	def file_ls(self, multihash, **kwargs):
		"""Deprecated method: Replace usages with the similar “client.ls”"""
		warnings.warn(
			"IPFS API function “file_ls” support is highly deprecated and will "
			"be removed soon from go-ipfs, use plain “ls” instead", FutureWarning
		)
		
		args = (multihash,)
		return self._client.request('/file/ls', args, decoder='json', **kwargs)


	# Dropped utility methods
	def add_pyobj(self, py_obj, **kwargs):
		"""Adds a picklable Python object as a file to IPFS.

		.. deprecated:: 0.4.2
		   The ``*_pyobj`` APIs allow for arbitrary code execution if abused.
		   Either switch to :meth:`~ipfsapi.Client.add_json` or use
		   ``client.add_bytes(pickle.dumps(py_obj))`` instead.

		Please see :meth:`~ipfsapi.Client.get_pyobj` for the
		**security risks** of using these methods!

		.. code-block:: python

			>>> c.add_pyobj([0, 1.0, 2j, '3', 4e5])
			'QmWgXZSUTNNDD8LdkdJ8UXSn55KfFnNvTP1r7SyaQd74Ji'

		Parameters
		----------
		py_obj : object
			A picklable Python object

		Returns
		-------
			str : Hash of the added IPFS object
		"""
		warnings.warn("Using `*_pyobj` on untrusted data is a security risk",
		              DeprecationWarning)
		return self.add_bytes(encoding.Pickle().encode(py_obj), **kwargs)

	def get_pyobj(self, multihash, **kwargs):
		"""Loads a pickled Python object from IPFS.

		.. deprecated:: 0.4.2
		   The ``*_pyobj`` APIs allow for arbitrary code execution if abused.
		   Either switch to :meth:`~ipfsapi.Client.get_json` or use
		   ``pickle.loads(client.cat(multihash))`` instead.

		.. caution::

			The pickle module is not intended to be secure against erroneous or
			maliciously constructed data. Never unpickle data received from an
			untrusted or unauthenticated source.

			Please **read**
			`this article <https://www.cs.uic.edu/%7Es/musings/pickle/>`_ to
			understand the security risks of using this method!

		.. code-block:: python

			>>> c.get_pyobj('QmWgXZSUTNNDD8LdkdJ8UXSn55KfFnNvTP1r7SyaQd74Ji')
			[0, 1.0, 2j, '3', 400000.0]

		Parameters
		----------
		multihash : str
			Multihash of the IPFS object to load

		Returns
		-------
			object : Deserialized IPFS Python object
		"""
		warnings.warn("Using `*_pyobj` on untrusted data is a security risk",
		              DeprecationWarning)
		return encoding.Pickle().parse(self.cat(multihash, **kwargs))
