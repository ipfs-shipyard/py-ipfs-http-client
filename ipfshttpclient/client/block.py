# -*- coding: utf-8 -*-
from __future__ import absolute_import

from . import base

from .. import multipart


class Section(base.SectionBase):
	"""
	Functions for interacting with raw IPFS blocks.
	"""

	def get(self, cid, **kwargs):
		r"""Returns the raw contents of a block.

		.. code-block:: python

			>>> client.block.get('QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDxdXBFca7D')
			b'\x121\n"\x12 \xdaW>\x14\xe5\xc1\xf6\xe4\x92\xd1 … \n\x02\x08\x01'

		Parameters
		----------
		cid : Union[str, cid.CIDv0, cid.CIDv1]
			The CID of an existing block to get

		Returns
		-------
			bytes
				Contents of the requested block
		"""
		args = (str(cid),)
		return self._client.request('/block/get', args, **kwargs)
	
	
	@base.returns_single_item
	def put(self, file, **kwargs):
		"""Stores the contents of the given file object as an IPFS block.

		.. code-block:: python

			>>> client.block.put(io.BytesIO(b'Mary had a little lamb'))
				{'Key':  'QmeV6C6XVt1wf7V7as7Yak3mxPma8jzpqyhtRtCvpKcfBb',
				 'Size': 22}

		Parameters
		----------
		file : Union[str, bytes, os.PathLike, io.IOBase, int]
			The data to be stored as an IPFS block

		Returns
		-------
			dict
				Information about the new block
				
				See :meth:`~ipfshttpclient.Client.block.stat`
		"""
		body, headers = multipart.stream_files(file, self.chunk_size)
		return self._client.request('/block/put', decoder='json', data=body,
		                            headers=headers, **kwargs)
	
	
	@base.returns_single_item
	def stat(self, cid, **kwargs):
		"""Returns a dict with the size of the block with the given hash.

		.. code-block:: python

			>>> client.block.stat('QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDxdXBFca7D')
			{'Key':  'QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDxdXBFca7D',
			 'Size': 258}

		Parameters
		----------
		cid : Union[str, cid.CIDv0, cid.CIDv1]
			The CID of an existing block to stat

		Returns
		-------
			dict
				Information about the requested block
		"""
		args = (str(cid),)
		return self._client.request('/block/stat', args, decoder='json', **kwargs)