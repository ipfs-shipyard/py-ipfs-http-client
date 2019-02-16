# -*- coding: utf-8 -*-
from __future__ import absolute_import

from . import base


class Section(base.SectionBase):
	@base.returns_single_item
	def wantlist(self, peer=None, **kwargs):
		"""Returns blocks currently on the bitswap wantlist.
		
		.. code-block:: python
			
			>>> client.bitswap.wantlist()
			{'Keys': [
				'QmeV6C6XVt1wf7V7as7Yak3mxPma8jzpqyhtRtCvpKcfBb',
				'QmdCWFLDXqgdWQY9kVubbEHBbkieKd3uo7MtCm7nTZZE9K',
				'QmVQ1XvYGF19X4eJqz1s7FJYJqAxFC4oqh3vWJJEXn66cp'
			]}
		
		Parameters
		----------
		peer : str
			Peer to show wantlist for.
		
		Returns
		-------
			dict
		
		+------+----------------------------------------------------+
		| Keys | List of blocks the connected daemon is looking for |
		+------+----------------------------------------------------+
		"""
		args = (peer,)
		return self._client.request('/bitswap/wantlist', args, decoder='json', **kwargs)
	
	
	@base.returns_single_item
	def stat(self, **kwargs):
		"""Returns some diagnostic information from the bitswap agent.
		
		.. code-block:: python
			
			>>> client.bitswap.stat()
			{'BlocksReceived': 96,
			 'DupBlksReceived': 73,
			 'DupDataReceived': 2560601,
			 'ProviderBufLen': 0,
			 'Peers': [
				'QmNZFQRxt9RMNm2VVtuV2Qx7q69bcMWRVXmr5CEkJEgJJP',
				'QmNfCubGpwYZAQxX8LQDsYgB48C4GbfZHuYdexpX9mbNyT',
				'QmNfnZ8SCs3jAtNPc8kf3WJqJqSoX7wsX7VqkLdEYMao4u',
				…
			 ],
			 'Wantlist': [
				'QmeV6C6XVt1wf7V7as7Yak3mxPma8jzpqyhtRtCvpKcfBb',
				'QmdCWFLDXqgdWQY9kVubbEHBbkieKd3uo7MtCm7nTZZE9K',
				'QmVQ1XvYGF19X4eJqz1s7FJYJqAxFC4oqh3vWJJEXn66cp'
			 ]
			}
		
		Returns
		-------
			dict
				Statistics, peers and wanted blocks
		"""
		return self._client.request('/bitswap/stat', decoder='json', **kwargs)