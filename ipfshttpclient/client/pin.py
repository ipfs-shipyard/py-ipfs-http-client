# -*- coding: utf-8 -*-
from __future__ import absolute_import

from . import base


class Section(base.SectionBase):
	@base.returns_single_item
	def add(self, path, *paths, **kwargs):
		"""Pins objects to local storage.

		Stores an IPFS object(s) from a given path locally to disk.

		.. code-block:: python

			>>> client.pin.add("QmfZY61ukoQuCX8e5Pt7v8pRfhkyxwZKZMTodAtmvyGZ5d")
			{'Pins': ['QmfZY61ukoQuCX8e5Pt7v8pRfhkyxwZKZMTodAtmvyGZ5d']}

		Parameters
		----------
		path : str
			Path to object(s) to be pinned
		recursive : bool
			Recursively unpin the object linked to by the specified object(s)

		Returns
		-------
			dict
		
		+------+-----------------------------------------------------------+
		| Pins | List of IPFS objects that have been pinned by this action |
		+------+-----------------------------------------------------------+
		"""
		#PY2: No support for kw-only parameters after glob parameters
		if "recursive" in kwargs:
			kwargs.setdefault("opts", {})["recursive"] = kwargs.pop("recursive")

		args = (path,) + paths
		return self._client.request('/pin/add', args, decoder='json', **kwargs)
	
	
	@base.returns_single_item
	def ls(self, *cids, **kwargs):
		"""Lists objects pinned to local storage.

		By default, all pinned objects are returned, but the ``type`` flag or
		arguments can restrict that to a specific pin type or to some specific
		objects respectively.

		.. code-block:: python

			>>> client.pin.ls()
			{'Keys': {
				'QmNNPMA1eGUbKxeph6yqV8ZmRkdVat … YMuz': {'Type': 'recursive'},
				'QmNPZUCeSN5458Uwny8mXSWubjjr6J … kP5e': {'Type': 'recursive'},
				'QmNg5zWpRMxzRAVg7FTQ3tUxVbKj8E … gHPz': {'Type': 'indirect'},
				…
				'QmNiuVapnYCrLjxyweHeuk6Xdqfvts … wCCe': {'Type': 'indirect'}
			}}

			>>> client.pin.ls('/ipfs/QmNNPMA1eGUbKxeph6yqV8ZmRkdVat … YMuz')
			{'Keys': {
				'QmNNPMA1eGUbKxeph6yqV8ZmRkdVat … YMuz': {'Type': 'recursive'}}}

			>>> client.pin.ls('/ipfs/QmdBCSn4UJP82MjhRVwpABww48tXL3 … mA6z')
			ipfshttpclient.exceptions.ErrorResponse:
				path '/ipfs/QmdBCSn4UJP82MjhRVwpABww48tXL3 … mA6z' is not pinned

		Parameters
		----------
		cids : str
			The path(s) of pinned IPFS object(s) to search for.
			If none are passed, return information about all pinned objects.
			If any of the passed CIDs is not pinned, then remote will
			return an error and an ErrorResponse exception will be raised.
		type : "str"
			The type of pinned keys to list. Can be:

			 * ``"direct"``
			 * ``"indirect"``
			 * ``"recursive"``
			 * ``"all"``

		Raises
		------
		~ipfsapi.exceptions.ErrorResponse
			Remote returned an error. Remote will return an error
			if any of the passed CIDs is not pinned. In this case,
			the exception will contain 'not pinned' in its args[0].

		Returns
		-------
			dict
		
		+------+--------------------------------------------------------------+
		| Keys | Mapping of IPFS object names currently pinned to their types |
		+------+--------------------------------------------------------------+
		"""
		#PY2: No support for kw-only parameters after glob parameters
		opts = {
			"type": kwargs.pop("type", "all")
		}
		kwargs.setdefault("opts", {}).update(opts)

		return self._client.request('/pin/ls', cids, decoder='json', **kwargs)


	@base.returns_single_item
	def rm(self, path, *paths, **kwargs):
		"""Removes a pinned object from local storage.

		Removes the pin from the given object allowing it to be garbage
		collected if needed.

		.. code-block:: python

			>>> client.pin.rm('QmfZY61ukoQuCX8e5Pt7v8pRfhkyxwZKZMTodAtmvyGZ5d')
			{'Pins': ['QmfZY61ukoQuCX8e5Pt7v8pRfhkyxwZKZMTodAtmvyGZ5d']}

		Parameters
		----------
		path : str
			Path to object(s) to be unpinned
		recursive : bool
			Recursively unpin the object linked to by the specified object(s)

		Returns
		-------
			dict
		
		+------+-------------------------------------------------------------+
		| Pins | List of IPFS objects that have been unpinned by this action |
		+------+-------------------------------------------------------------+
		"""
		#PY2: No support for kw-only parameters after glob parameters
		if "recursive" in kwargs:
			kwargs.setdefault("opts", {})["recursive"] = kwargs.pop("recursive")

		args = (path,) + paths
		return self._client.request('/pin/rm', args, decoder='json', **kwargs)
	
	
	@base.returns_single_item
	def update(self, from_path, to_path, **kwargs):
		"""Replaces one pin with another.

		Updates one pin to another, making sure that all objects in the new pin
		are local. Then removes the old pin. This is an optimized version of
		using first using :meth:`~ipfshttpclient.Client.pin.add` to add a new pin
		for an object and then using :meth:`~ipfshttpclient.Client.pin.rm` to remove
		the pin for the old object.

		.. code-block:: python

			>>> client.pin.update("QmXMqez83NU77ifmcPs5CkNRTMQksBLkyfBf4H5g1NZ52P",
			...              "QmUykHAi1aSjMzHw3KmBoJjqRUQYNkFXm8K1y7ZsJxpfPH")
			{"Pins": ["/ipfs/QmXMqez83NU77ifmcPs5CkNRTMQksBLkyfBf4H5g1NZ52P",
					  "/ipfs/QmUykHAi1aSjMzHw3KmBoJjqRUQYNkFXm8K1y7ZsJxpfPH"]}

		Parameters
		----------
		from_path : str
			Path to the old object
		to_path : str
			Path to the new object to be pinned
		unpin : bool
			Should the pin of the old object be removed? (Default: ``True``)

		Returns
		-------
			dict
		
		+------+-------------------------------------------------------------+
		| Pins | List of IPFS objects that have been affected by this action |
		+------+-------------------------------------------------------------+
		"""
		#PY2: No support for kw-only parameters after glob parameters
		if "unpin" in kwargs:
			kwargs.setdefault("opts", {})["unpin"] = kwargs.pop("unpin")

		args = (from_path, to_path)
		return self._client.request('/pin/update', args, decoder='json', **kwargs)


	def verify(self, path, *paths, **kwargs):
		"""Verify that recursive pins are complete.

		Scan the repo for pinned object graphs and check their integrity.
		Issues will be reported back with a helpful human-readable error
		message to aid in error recovery. This is useful to help recover
		from datastore corruptions (such as when accidentally deleting
		files added using the filestore backend).

		This function returns an iterator needs to be closed using a context
		manager (``with``-statement) or using the ``.close()`` method.

		.. code-block:: python

			>>> with client.pin.verify("QmN…TTZ", verbose=True) as pin_verify_iter:
			...     for item in pin_verify_iter:
			...         print(item)
			...
			{"Cid":"QmVkNdzCBukBRdpyFiKPyL2R15qPExMr9rV9RFV2kf9eeV","Ok":True}
			{"Cid":"QmbPzQruAEFjUU3gQfupns6b8USr8VrD9H71GrqGDXQSxm","Ok":True}
			{"Cid":"Qmcns1nUvbeWiecdGDPw8JxWeUfxCV8JKhTfgzs3F8JM4P","Ok":True}
			…

		Parameters
		----------
		path : str
			Path to object(s) to be checked
		verbose : bool
			Also report status of items that were OK? (Default: ``False``)

		Returns
		-------
			Iterable[dict]
		
		+-----+----------------------------------------------------+
		| Cid | IPFS object ID checked                             |
		+-----+----------------------------------------------------+
		| Ok  | Whether the given object was successfully verified |
		+-----+----------------------------------------------------+
		"""
		#PY2: No support for kw-only parameters after glob parameters
		if "verbose" in kwargs:
			kwargs.setdefault("opts", {})["verbose"] = kwargs.pop("verbose")

		args = (path,) + paths
		return self._client.request('/pin/verify', args, decoder='json', stream=True, **kwargs)