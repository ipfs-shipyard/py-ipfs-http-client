# -*- coding: utf-8 -*-
from __future__ import absolute_import

from . import base


class Section(base.SectionBase):
	@base.returns_single_item
	def add(self, peer, *peers, **kwargs):
		"""Adds peers to the bootstrap list.

		Parameters
		----------
		peer : str
			IPFS MultiAddr of a peer to add to the list

		Returns
		-------
			dict
		"""
		args = (peer,) + peers
		return self._client.request('/bootstrap/add', args, decoder='json', **kwargs)
	
	
	@base.returns_single_item
	def list(self, **kwargs):
		"""Returns the addresses of peers used during initial discovery of the
		IPFS network.

		Peers are output in the format ``<multiaddr>/<peerID>``.

		.. code-block:: python

			>>> client.bootstrap.list()
			{'Peers': [
				'/ip4/104.131.131.82/tcp/4001/ipfs/QmaCpDMGvV2BGHeYER … uvuJ',
				'/ip4/104.236.176.52/tcp/4001/ipfs/QmSoLnSGccFuZQJzRa … ca9z',
				'/ip4/104.236.179.241/tcp/4001/ipfs/QmSoLPppuBtQSGwKD … KrGM',
				…
				'/ip4/178.62.61.185/tcp/4001/ipfs/QmSoLMeWqB7YGVLJN3p … QBU3'
			]}

		Returns
		-------
			dict
		
		+-------+-------------------------------+
		| Peers | List of known bootstrap peers |
		+-------+-------------------------------+
		"""
		return self._client.request('/bootstrap', decoder='json', **kwargs)
	
	
	@base.returns_single_item
	def rm(self, peer, *peers, **kwargs):
		"""Removes peers from the bootstrap list.

		Parameters
		----------
		peer : str
			IPFS MultiAddr of a peer to remove from the list

		Returns
		-------
			dict
		"""
		args = (peer,) + peers
		return self._client.request('/bootstrap/rm', args, decoder='json', **kwargs)