# -*- coding: utf-8 -*-
from __future__ import absolute_import

import ipfsapi.multipart

from . import base


class ObjectPatchSection(base.SectionBase):
	def add_link(self, root, name, ref, create=False, **kwargs):
		"""Creates a new merkledag object based on an existing one.

		The new object will have a link to the provided object.

		.. code-block:: python

			>>> c.object.patch.add_link(
			...     'QmR79zQQj2aDfnrNgczUhvf2qWapEfQ82YQRt3QjrbhSb2',
			...     'Johnny',
			...     'QmR79zQQj2aDfnrNgczUhvf2qWapEfQ82YQRt3QjrbhSb2'
			... )
			{'Hash': 'QmNtXbF3AjAk59gQKRgEdVabHcSsiPUnJwHnZKyj2x8Z3k'}

		Parameters
		----------
		root : str
			IPFS hash for the object being modified
		name : str
			name for the new link
		ref : str
			IPFS hash for the object being linked to
		create : bool
			Create intermediary nodes

		Returns
		-------
			dict : Hash of new object
		"""
		kwargs.setdefault("opts", {"create": create})

		args = ((root, name, ref),)
		return self._client.request('/object/patch/add-link', args, decoder='json', **kwargs)


	def append_data(self, multihash, new_data, **kwargs):
		"""Creates a new merkledag object based on an existing one.

		The new object will have the provided data appended to it,
		and will thus have a new Hash.

		.. code-block:: python

			>>> c.object.patch.append_data("QmZZmY … fTqm", io.BytesIO(b"bla"))
			{'Hash': 'QmR79zQQj2aDfnrNgczUhvf2qWapEfQ82YQRt3QjrbhSb2'}

		Parameters
		----------
		multihash : str
			The hash of an ipfs object to modify
		new_data : io.RawIOBase
			The data to append to the object's data section

		Returns
		-------
			dict : Hash of new object
		"""
		args = (multihash,)
		body, headers = ipfsapi.multipart.stream_files(new_data, self.chunk_size)
		return self._client.request('/object/patch/append-data', args, decoder='json',
		                            data=body, headers=headers, **kwargs)


	def rm_link(self, root, link, **kwargs):
		"""Creates a new merkledag object based on an existing one.

		The new object will lack a link to the specified object.

		.. code-block:: python

			>>> c.object.patch.rm_link(
			...     'QmNtXbF3AjAk59gQKRgEdVabHcSsiPUnJwHnZKyj2x8Z3k',
			...     'Johnny'
			... )
			{'Hash': 'QmR79zQQj2aDfnrNgczUhvf2qWapEfQ82YQRt3QjrbhSb2'}

		Parameters
		----------
		root : str
			IPFS hash of the object to modify
		link : str
			name of the link to remove

		Returns
		-------
			dict : Hash of new object
		"""
		args = ((root, link),)
		return self._client.request('/object/patch/rm-link', args, decoder='json', **kwargs)


	def set_data(self, root, data, **kwargs):
		"""Creates a new merkledag object based on an existing one.

		The new object will have the same links as the old object but
		with the provided data instead of the old object's data contents.

		.. code-block:: python

			>>> c.object.patch.set_data(
			...     'QmNtXbF3AjAk59gQKRgEdVabHcSsiPUnJwHnZKyj2x8Z3k',
			...     io.BytesIO(b'bla')
			... )
			{'Hash': 'QmSw3k2qkv4ZPsbu9DVEJaTMszAQWNgM1FTFYpfZeNQWrd'}

		Parameters
		----------
		root : str
			IPFS hash of the object to modify
		data : io.RawIOBase
			The new data to store in root

		Returns
		-------
			dict : Hash of new object
		"""
		args = (root,)
		body, headers = ipfsapi.multipart.stream_files(data, self.chunk_size)
		return self._client.request('/object/patch/set-data', args, decoder='json', data=body,
		                            headers=headers, **kwargs)



class ObjectSection(base.SectionBase):
	patch = base.SectionProperty(ObjectPatchSection)


	def data(self, multihash, **kwargs):
		r"""Returns the raw bytes in an IPFS object.

		.. code-block:: python

			>>> c.object.data('QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDxdXBFca7D')
			b'\x08\x01'

		Parameters
		----------
		multihash : str
			Key of the object to retrieve, in base58-encoded multihash format

		Returns
		-------
			str : Raw object data
		"""
		args = (multihash,)
		return self._client.request('/object/data', args, **kwargs)


	def get(self, multihash, **kwargs):
		"""Get and serialize the DAG node named by multihash.

		.. code-block:: python

			>>> c.object.get('QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDxdXBFca7D')
			{'Data': '\x08\x01',
			 'Links': [
				{'Hash': 'Qmd2xkBfEwEs9oMTk77A6jrsgurpF3ugXSg7dtPNFkcNMV',
				 'Name': 'Makefile',          'Size': 174},
				{'Hash': 'QmeKozNssnkJ4NcyRidYgDY2jfRZqVEoRGfipkgath71bX',
				 'Name': 'example',           'Size': 1474},
				{'Hash': 'QmZAL3oHMQYqsV61tGvoAVtQLs1WzRe1zkkamv9qxqnDuK',
				 'Name': 'home',              'Size': 3947},
				{'Hash': 'QmZNPyKVriMsZwJSNXeQtVQSNU4v4KEKGUQaMT61LPahso',
				 'Name': 'lib',               'Size': 268261},
				{'Hash': 'QmSY8RfVntt3VdxWppv9w5hWgNrE31uctgTiYwKir8eXJY',
				 'Name': 'published-version', 'Size': 55}]}

		Parameters
		----------
		multihash : str
			Key of the object to retrieve, in base58-encoded multihash format

		Returns
		-------
			dict : Object data and links
		"""
		args = (multihash,)
		return self._client.request('/object/get', args, decoder='json', **kwargs)


	def links(self, multihash, **kwargs):
		"""Returns the links pointed to by the specified object.

		.. code-block:: python

			>>> c.object.links('QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDx … ca7D')
			{'Hash': 'QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDxdXBFca7D',
			 'Links': [
				{'Hash': 'Qmd2xkBfEwEs9oMTk77A6jrsgurpF3ugXSg7dtPNFkcNMV',
				 'Name': 'Makefile',          'Size': 174},
				{'Hash': 'QmeKozNssnkJ4NcyRidYgDY2jfRZqVEoRGfipkgath71bX',
				 'Name': 'example',           'Size': 1474},
				{'Hash': 'QmZAL3oHMQYqsV61tGvoAVtQLs1WzRe1zkkamv9qxqnDuK',
				 'Name': 'home',              'Size': 3947},
				{'Hash': 'QmZNPyKVriMsZwJSNXeQtVQSNU4v4KEKGUQaMT61LPahso',
				 'Name': 'lib',               'Size': 268261},
				{'Hash': 'QmSY8RfVntt3VdxWppv9w5hWgNrE31uctgTiYwKir8eXJY',
				 'Name': 'published-version', 'Size': 55}]}

		Parameters
		----------
		multihash : str
			Key of the object to retrieve, in base58-encoded multihash format

		Returns
		-------
			dict : Object hash and merkedag links
		"""
		args = (multihash,)
		return self._client.request('/object/links', args, decoder='json', **kwargs)


	def new(self, template=None, **kwargs):
		"""Creates a new object from an IPFS template.

		By default this creates and returns a new empty merkledag node, but you
		may pass an optional template argument to create a preformatted node.

		.. code-block:: python

			>>> c.object.new()
			{'Hash': 'QmdfTbBqBPQ7VNxZEYEj14VmRuZBkqFbiwReogJgS1zR1n'}

		Parameters
		----------
		template : str
			Blueprints from which to construct the new object. Possible values:

			 * ``"unixfs-dir"``
			 * ``None``

		Returns
		-------
			dict : Object hash
		"""
		args = (template,) if template is not None else ()
		return self._client.request('/object/new', args, decoder='json', **kwargs)


	def put(self, file, **kwargs):
		"""Stores input as a DAG object and returns its key.

		.. code-block:: python

			>>> c.object.put(io.BytesIO(b'''
			...       {
			...           "Data": "another",
			...           "Links": [ {
			...               "Name": "some link",
			...               "Hash": "QmXg9Pp2ytZ14xgmQjYEiHjVjMFXzCV … R39V",
			...               "Size": 8
			...           } ]
			...       }'''))
			{'Hash': 'QmZZmY4KCu9r3e7M2Pcn46Fc5qbn6NpzaAGaYb22kbfTqm',
			 'Links': [
				{'Hash': 'QmXg9Pp2ytZ14xgmQjYEiHjVjMFXzCVVEcRTWJBmLgR39V',
				 'Size': 8, 'Name': 'some link'}
			 ]
			}

		Parameters
		----------
		file : io.RawIOBase
			(JSON) object from which the DAG object will be created

		Returns
		-------
			dict : Hash and links of the created DAG object

				   See :meth:`~ipfsapi.Client.object.links`
		"""
		body, headers = ipfsapi.multipart.stream_files(file, self.chunk_size)
		return self._client.request('/object/put', decoder='json', data=body,
		                            headers=headers, **kwargs)


	def stat(self, multihash, **kwargs):
		"""Get stats for the DAG node named by multihash.

		.. code-block:: python

			>>> c.object.stat('QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDxdXBFca7D')
			{'LinksSize': 256, 'NumLinks': 5,
			 'Hash': 'QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDxdXBFca7D',
			 'BlockSize': 258, 'CumulativeSize': 274169, 'DataSize': 2}

		Parameters
		----------
		multihash : str
			Key of the object to retrieve, in base58-encoded multihash format

		Returns
		-------
			dict
		"""
		args = (multihash,)
		return self._client.request('/object/stat', args, decoder='json', **kwargs)



class PinSection(base.SectionBase):
	def add(self, path, *paths, **kwargs):
		"""Pins objects to local storage.

		Stores an IPFS object(s) from a given path locally to disk.

		.. code-block:: python

			>>> c.pin.add("QmfZY61ukoQuCX8e5Pt7v8pRfhkyxwZKZMTodAtmvyGZ5d")
			{'Pins': ['QmfZY61ukoQuCX8e5Pt7v8pRfhkyxwZKZMTodAtmvyGZ5d']}

		Parameters
		----------
		path : str
			Path to object(s) to be pinned
		recursive : bool
			Recursively unpin the object linked to by the specified object(s)

		Returns
		-------
			dict : List of IPFS objects that have been pinned
		"""
		#PY2: No support for kw-only parameters after glob parameters
		if "recursive" in kwargs:
			kwargs.setdefault("opts", {"recursive": kwargs.pop("recursive")})

		args = (path,) + paths
		return self._client.request('/pin/add', args, decoder='json', **kwargs)


	def ls(self, type="all", **kwargs):
		"""Lists objects pinned to local storage.

		By default, all pinned objects are returned, but the ``type`` flag or
		arguments can restrict that to a specific pin type or to some specific
		objects respectively.

		.. code-block:: python

			>>> c.pin.ls()
			{'Keys': {
				'QmNNPMA1eGUbKxeph6yqV8ZmRkdVat … YMuz': {'Type': 'recursive'},
				'QmNPZUCeSN5458Uwny8mXSWubjjr6J … kP5e': {'Type': 'recursive'},
				'QmNg5zWpRMxzRAVg7FTQ3tUxVbKj8E … gHPz': {'Type': 'indirect'},
				…
				'QmNiuVapnYCrLjxyweHeuk6Xdqfvts … wCCe': {'Type': 'indirect'}}}

		Parameters
		----------
		type : "str"
			The type of pinned keys to list. Can be:

			 * ``"direct"``
			 * ``"indirect"``
			 * ``"recursive"``
			 * ``"all"``

		Returns
		-------
			dict : Hashes of pinned IPFS objects and why they are pinned
		"""
		kwargs.setdefault("opts", {"type": type})

		return self._client.request('/pin/ls', decoder='json', **kwargs)


	def rm(self, path, *paths, **kwargs):
		"""Removes a pinned object from local storage.

		Removes the pin from the given object allowing it to be garbage
		collected if needed.

		.. code-block:: python

			>>> c.pin.rm('QmfZY61ukoQuCX8e5Pt7v8pRfhkyxwZKZMTodAtmvyGZ5d')
			{'Pins': ['QmfZY61ukoQuCX8e5Pt7v8pRfhkyxwZKZMTodAtmvyGZ5d']}

		Parameters
		----------
		path : str
			Path to object(s) to be unpinned
		recursive : bool
			Recursively unpin the object linked to by the specified object(s)

		Returns
		-------
			dict : List of IPFS objects that have been unpinned
		"""
		#PY2: No support for kw-only parameters after glob parameters
		if "recursive" in kwargs:
			kwargs.setdefault("opts", {"recursive": kwargs["recursive"]})
			del kwargs["recursive"]

		args = (path,) + paths
		return self._client.request('/pin/rm', args, decoder='json', **kwargs)


	def update(self, from_path, to_path, **kwargs):
		"""Replaces one pin with another.

		Updates one pin to another, making sure that all objects in the new pin
		are local. Then removes the old pin. This is an optimized version of
		using first using :meth:`~ipfsapi.Client.pin.add` to add a new pin
		for an object and then using :meth:`~ipfsapi.Client.pin.rm` to remove
		the pin for the old object.

		.. code-block:: python

			>>> c.pin.update("QmXMqez83NU77ifmcPs5CkNRTMQksBLkyfBf4H5g1NZ52P",
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
			dict : List of IPFS objects affected by the pinning operation
		"""
		#PY2: No support for kw-only parameters after glob parameters
		if "unpin" in kwargs:
			kwargs.setdefault("opts", {"unpin": kwargs["unpin"]})
			del kwargs["unpin"]

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

			>>> with c.pin.verify("QmN…TTZ", verbose=True) as pin_verify_iter:
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
			iterable
		"""
		#PY2: No support for kw-only parameters after glob parameters
		if "verbose" in kwargs:
			kwargs.setdefault("opts", {"verbose": kwargs["verbose"]})
			del kwargs["verbose"]

		args = (path,) + paths
		return self._client.request('/pin/verify', args, decoder='json', stream=True, **kwargs)


class RefsSection(base.SectionBase):
	def __call__(self, multihash, **kwargs):
		"""Returns a list of hashes of objects referenced by the given hash.

		.. code-block:: python

			>>> c.refs('QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDxdXBFca7D')
			[{'Ref': 'Qmd2xkBfEwEs9oMTk77A6jrsgurpF3ugXSg7 … cNMV', 'Err': ''},
			 …
			 {'Ref': 'QmSY8RfVntt3VdxWppv9w5hWgNrE31uctgTi … eXJY', 'Err': ''}]

		Parameters
		----------
		multihash : str
			Path to the object(s) to list refs from

		Returns
		-------
			list
		"""
		args = (multihash,)
		return self._client.request('/refs', args, decoder='json', **kwargs)


	def local(self, **kwargs):
		"""Displays the hashes of all local objects.

		.. code-block:: python

			>>> c.refs.local()
			[{'Ref': 'Qmd2xkBfEwEs9oMTk77A6jrsgurpF3ugXSg7 … cNMV', 'Err': ''},
			 …
			 {'Ref': 'QmSY8RfVntt3VdxWppv9w5hWgNrE31uctgTi … eXJY', 'Err': ''}]

		Returns
		-------
			list
		"""
		return self._client.request('/refs/local', decoder='json', **kwargs)


class GraphBase(base.ClientBase):
	#XXX: Implement `dag.*`
	object = base.SectionProperty(ObjectSection)
	pin    = base.SectionProperty(PinSection)
	refs   = base.SectionProperty(RefsSection)

	# Aliases for previous method names
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

	refs_local = base.DeprecatedMethodProperty("refs", "local")
