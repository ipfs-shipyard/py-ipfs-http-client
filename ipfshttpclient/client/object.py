# -*- coding: utf-8 -*-
from __future__ import absolute_import

from . import base

from .. import multipart


class PatchSection(base.SectionBase):
	@base.returns_single_item
	def add_link(self, root, name, ref, create=False, **kwargs):
		"""Creates a new merkledag object based on an existing one.

		The new object will have a link to the provided object.

		.. code-block:: python

			>>> client.object.patch.add_link(
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
			dict
		
		+------+----------------------------------+
		| Hash | Hash of the newly derived object |
		+------+----------------------------------+
		"""
		kwargs.setdefault("opts", {})["create"] = create

		args = ((root, name, ref),)
		return self._client.request('/object/patch/add-link', args, decoder='json', **kwargs)
	
	
	@base.returns_single_item
	def append_data(self, cid, new_data, **kwargs):
		"""Creates a new merkledag object based on an existing one.

		The new object will have the provided data appended to it,
		and will thus have a new Hash.

		.. code-block:: python

			>>> client.object.patch.append_data("QmZZmY … fTqm", io.BytesIO(b"bla"))
			{'Hash': 'QmR79zQQj2aDfnrNgczUhvf2qWapEfQ82YQRt3QjrbhSb2'}

		Parameters
		----------
		cid : Union[str, cid.CIDv0, cid.CIDv1]
			The hash of an ipfs object to modify
		new_data : Union[str, bytes, os.PathLike, io.IOBase, int]
			The data to append to the object's data section

		Returns
		-------
			dict
		
		+------+----------------------------------+
		| Hash | Hash of the newly derived object |
		+------+----------------------------------+
		"""
		args = (str(cid),)
		body, headers = multipart.stream_files(new_data, self.chunk_size)
		return self._client.request('/object/patch/append-data', args, decoder='json',
		                            data=body, headers=headers, **kwargs)
	
	
	@base.returns_single_item
	def rm_link(self, root, link, **kwargs):
		"""Creates a new merkledag object based on an existing one.

		The new object will lack a link to the specified object.

		.. code-block:: python

			>>> client.object.patch.rm_link(
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
			dict
		
		+------+----------------------------------+
		| Hash | Hash of the newly derived object |
		+------+----------------------------------+
		"""
		args = ((root, link),)
		return self._client.request('/object/patch/rm-link', args, decoder='json', **kwargs)
	
	
	@base.returns_single_item
	def set_data(self, root, data, **kwargs):
		"""Creates a new merkledag object based on an existing one.

		The new object will have the same links as the old object but
		with the provided data instead of the old object's data contents.

		.. code-block:: python

			>>> client.object.patch.set_data(
			...     'QmNtXbF3AjAk59gQKRgEdVabHcSsiPUnJwHnZKyj2x8Z3k',
			...     io.BytesIO(b'bla')
			... )
			{'Hash': 'QmSw3k2qkv4ZPsbu9DVEJaTMszAQWNgM1FTFYpfZeNQWrd'}

		Parameters
		----------
		root : str
			IPFS hash of the object to modify
		data : Union[str, bytes, os.PathLike, io.IOBase, int]
			The new data to store in root

		Returns
		-------
			dict
		
		+------+----------------------------------+
		| Hash | Hash of the newly derived object |
		+------+----------------------------------+
		"""
		args = (root,)
		body, headers = multipart.stream_files(data, self.chunk_size)
		return self._client.request('/object/patch/set-data', args, decoder='json', data=body,
		                            headers=headers, **kwargs)



class Section(base.SectionBase):
	patch = base.SectionProperty(PatchSection)
	
	
	def data(self, cid, **kwargs):
		r"""Returns the raw bytes in an IPFS object.

		.. code-block:: python

			>>> client.object.data('QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDxdXBFca7D')
			b'\x08\x01'

		Parameters
		----------
		cid : Union[str, cid.CIDv0, cid.CIDv1]
			Key of the object to retrieve, in CID format

		Returns
		-------
			bytes
				Raw object data
		"""
		args = (str(cid),)
		return self._client.request('/object/data', args, **kwargs)
	
	
	@base.returns_single_item
	def get(self, cid, **kwargs):
		"""Get and serialize the DAG node named by CID.
		
		.. code-block:: python

			>>> client.object.get('QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDxdXBFca7D')
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
				 'Name': 'published-version', 'Size': 55}
			]}

		Parameters
		----------
		cid : Union[str, cid.CIDv0, cid.CIDv1]
			Key of the object to retrieve, in CID format

		Returns
		-------
			dict
		
		+-------+------------------------------------------------+
		| Data  | Raw object data (ISO-8859-1 decoded)           |
		+-------+------------------------------------------------+
		| Links | List of links associated with the given object |
		+-------+------------------------------------------------+
		"""
		args = (str(cid),)
		return self._client.request('/object/get', args, decoder='json', **kwargs)
	
	
	@base.returns_single_item
	def links(self, cid, **kwargs):
		"""Returns the links pointed to by the specified object.

		.. code-block:: python

			>>> client.object.links('QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDx … ca7D')
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
		cid : Union[str, cid.CIDv0, cid.CIDv1]
			Key of the object to retrieve, in CID format

		Returns
		-------
			dict
		
		+-------+------------------------------------------------+
		| Hash  | The requested object CID                       |
		+-------+------------------------------------------------+
		| Links | List of links associated with the given object |
		+-------+------------------------------------------------+
		"""
		args = (str(cid),)
		return self._client.request('/object/links', args, decoder='json', **kwargs)
	
	
	@base.returns_single_item
	def new(self, template=None, **kwargs):
		"""Creates a new object from an IPFS template.

		By default this creates and returns a new empty merkledag node, but you
		may pass an optional template argument to create a preformatted node.

		.. code-block:: python

			>>> client.object.new()
			{'Hash': 'QmdfTbBqBPQ7VNxZEYEj14VmRuZBkqFbiwReogJgS1zR1n'}

		Parameters
		----------
		template : str
			Blueprints from which to construct the new object. Possible values:

			 * ``"unixfs-dir"``
			 * ``None``

		Returns
		-------
			dict
		
		+-------+----------------------------------------+
		| Hash  | The hash of the requested empty object |
		+-------+----------------------------------------+
		"""
		args = (template,) if template is not None else ()
		return self._client.request('/object/new', args, decoder='json', **kwargs)
	
	
	@base.returns_single_item
	def put(self, file, **kwargs):
		"""Stores input as a DAG object and returns its key.

		.. code-block:: python

			>>> client.object.put(io.BytesIO(b'''
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
		file : Union[str, bytes, os.PathLike, io.IOBase, int]
			(JSON) object from which the DAG object will be created

		Returns
		-------
			dict
				Hash and links of the created DAG object
				
				See the :meth:`~ipfshttpclient.Client.object.links` method for
				details.
		"""
		body, headers = multipart.stream_files(file, self.chunk_size)
		return self._client.request('/object/put', decoder='json', data=body,
		                            headers=headers, **kwargs)
	
	
	@base.returns_single_item
	def stat(self, cid, **kwargs):
		"""Get stats for the DAG node named by cid.

		.. code-block:: python

			>>> client.object.stat('QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDxdXBFca7D')
			{'LinksSize': 256, 'NumLinks': 5,
			 'Hash': 'QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDxdXBFca7D',
			 'BlockSize': 258, 'CumulativeSize': 274169, 'DataSize': 2}

		Parameters
		----------
		cid : Union[str, cid.CIDv0, cid.CIDv1]
			Key of the object to retrieve, in CID format

		Returns
		-------
			dict
		"""
		args = (str(cid),)
		return self._client.request('/object/stat', args, decoder='json', **kwargs)