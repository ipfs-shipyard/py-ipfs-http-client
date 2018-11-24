# -*- coding: utf-8 -*-
"""IPFS API Bindings for Python.

Classes:

 * Client – a TCP client for interacting with an IPFS daemon
"""
from __future__ import absolute_import

import os
import warnings

DEFAULT_HOST = str(os.environ.get("PY_IPFSAPI_DEFAULT_HOST", 'localhost'))
DEFAULT_PORT = int(os.environ.get("PY_IPFSAPI_DEFAULT_PORT", 5001))
DEFAULT_BASE = str(os.environ.get("PY_IPFSAPI_DEFAULT_BASE", 'api/v0'))

VERSION_MINIMUM = "0.4.3"
VERSION_MAXIMUM = "0.5.0"

from . import files
from . import graph
from . import crypto
from . import network
from . import node

import ipfsapi.multipart
from .. import utils, exceptions, encoding


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
            chunk_size=ipfsapi.multipart.default_chunk_size, **defaults):
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


class Client(
	files.FilesBase,
	graph.GraphBase,
	crypto.CryptoBase,
	network.NetworkBase,
	node.NodeBase
):
	def dns(self, domain_name, recursive=False, **kwargs):
		"""Resolves DNS links to the referenced object.

		Multihashes are hard to remember, but domain names are usually easy to
		remember. To create memorable aliases for multihashes, DNS TXT records
		can point to other DNS links, IPFS objects, IPNS keys, etc.
		This command resolves those links to the referenced object.

		For example, with this DNS TXT record::

			>>> import dns.resolver
			>>> a = dns.resolver.query("ipfs.io", "TXT")
			>>> a.response.answer[0].items[0].to_text()
			'"dnslink=/ipfs/QmTzQ1JRkWErjk39mryYw2WVaphAZNAREyMchXzYQ7c15n"'

		The resolver will give::

			>>> c.dns("ipfs.io")
			{'Path': '/ipfs/QmTzQ1JRkWErjk39mryYw2WVaphAZNAREyMchXzYQ7c15n'}

		Parameters
		----------
		domain_name : str
			The domain-name name to resolve
		recursive : bool
			Resolve until the name is not a DNS link

		Returns
		-------
			dict : Resource were a DNS entry points to
		"""
		kwargs.setdefault("opts", {"recursive": recursive})

		args = (domain_name,)
		return self._client.request('/dns', args, decoder='json', **kwargs)

	###########
	# HELPERS #
	###########

	@utils.return_field('Hash')
	def add_bytes(self, data, **kwargs):
		"""Adds a set of bytes as a file to IPFS.

		.. code-block:: python

			>>> c.add_bytes(b"Mary had a little lamb")
			'QmZfF6C9j4VtoCsTp4KSrhYH47QMd3DNXVZBKaxJdhaPab'

		Also accepts and will stream generator objects.

		Parameters
		----------
		data : bytes
			Content to be added as a file

		Returns
		-------
			str : Hash of the added IPFS object
		"""
		body, headers = ipfsapi.multipart.stream_bytes(data, self.chunk_size)
		return self._client.request('/add', decoder='json',
		                            data=body, headers=headers, **kwargs)

	@utils.return_field('Hash')
	def add_str(self, string, **kwargs):
		"""Adds a Python string as a file to IPFS.

		.. code-block:: python

			>>> c.add_str(u"Mary had a little lamb")
			'QmZfF6C9j4VtoCsTp4KSrhYH47QMd3DNXVZBKaxJdhaPab'

		Also accepts and will stream generator objects.

		Parameters
		----------
		string : str
			Content to be added as a file

		Returns
		-------
			str : Hash of the added IPFS object
		"""
		body, headers = ipfsapi.multipart.stream_text(string, self.chunk_size)
		return self._client.request('/add', decoder='json',
									data=body, headers=headers, **kwargs)

	def add_json(self, json_obj, **kwargs):
		"""Adds a json-serializable Python dict as a json file to IPFS.

		.. code-block:: python

			>>> c.add_json({'one': 1, 'two': 2, 'three': 3})
			'QmVz9g7m5u3oHiNKHj2CJX1dbG1gtismRS3g9NaPBBLbob'

		Parameters
		----------
		json_obj : dict
			A json-serializable Python dictionary

		Returns
		-------
			str : Hash of the added IPFS object
		"""
		return self.add_bytes(encoding.Json().encode(json_obj), **kwargs)

	def get_json(self, multihash, **kwargs):
		"""Loads a json object from IPFS.

		.. code-block:: python

			>>> c.get_json('QmVz9g7m5u3oHiNKHj2CJX1dbG1gtismRS3g9NaPBBLbob')
			{'one': 1, 'two': 2, 'three': 3}

		Parameters
		----------
		multihash : str
		   Multihash of the IPFS object to load

		Returns
		-------
			object : Deserialized IPFS JSON object value
		"""
		return self.cat(multihash, decoder='json', **kwargs)

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
		return self.cat(multihash, decoder='pickle', **kwargs)
