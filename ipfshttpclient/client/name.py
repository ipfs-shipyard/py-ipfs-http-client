# -*- coding: utf-8 -*-
from __future__ import absolute_import

from . import base


class Section(base.SectionBase):
	def publish(self, ipfs_path, resolve=True, lifetime="24h", ttl=None, key=None, **kwargs):
		"""Publishes an object to IPNS.

		IPNS is a PKI namespace, where names are the hashes of public keys, and
		the private key enables publishing new (signed) values. In publish, the
		default value of *name* is your own identity public key.

		.. code-block:: python

			>>> client.name.publish('/ipfs/QmfZY61ukoQuCX8e5Pt7v8pRfhkyxwZK … GZ5d')
			{'Value': '/ipfs/QmfZY61ukoQuCX8e5Pt7v8pRfhkyxwZKZMTodAtmvyGZ5d',
			 'Name': 'QmVgNoP89mzpgEAAqK8owYoDEyB97MkcGvoWZir8otE9Uc'}

		Parameters
		----------
		ipfs_path : str
			IPFS path of the object to be published
		resolve : bool
			Resolve given path before publishing
		lifetime : str
			Time duration that the record will be valid for

			Accepts durations such as ``"300s"``, ``"1.5h"`` or ``"2h45m"``.
			Valid units are:

			 * ``"ns"``
			 * ``"us"`` (or ``"µs"``)
			 * ``"ms"``
			 * ``"s"``
			 * ``"m"``
			 * ``"h"``
		ttl : string
			Time duration this record should be cached for.
			Same syntax like 'lifetime' option. (experimental feature)
		key : string
			 Name of the key to be used, as listed by 'ipfs key list'.

		Returns
		-------
			dict : IPNS hash and the IPFS path it points at
		"""
		opts = {"lifetime": lifetime, "resolve": resolve}
		if ttl:
			opts["ttl"] = ttl
		if key:
			opts["key"] = key
		kwargs.setdefault("opts", {}).update(opts)

		args = (ipfs_path,)
		return self._client.request('/name/publish', args, decoder='json', **kwargs)


	def resolve(self, name=None, recursive=False, nocache=False, **kwargs):
		"""Gets the value currently published at an IPNS name.

		IPNS is a PKI namespace, where names are the hashes of public keys, and
		the private key enables publishing new (signed) values. In resolve, the
		default value of ``name`` is your own identity public key.

		.. code-block:: python

			>>> client.name.resolve()
			{'Path': '/ipfs/QmfZY61ukoQuCX8e5Pt7v8pRfhkyxwZKZMTodAtmvyGZ5d'}

		Parameters
		----------
		name : str
			The IPNS name to resolve (defaults to the connected node)
		recursive : bool
			Resolve until the result is not an IPFS name (default: false)
		nocache : bool
			Do not use cached entries (default: false)

		Returns
		-------
			dict : The IPFS path the IPNS hash points at
		"""
		opts = {"recursive": recursive, "nocache": nocache}
		kwargs.setdefault("opts", {}).update(opts)
		args = (name,) if name is not None else ()
		return self._client.request('/name/resolve', args, decoder='json', **kwargs)