# -*- coding: utf-8 -*-
from __future__ import absolute_import

from . import base


class FiltersSection(base.SectionBase):
	@base.returns_single_item
	def add(self, address, *addresses, **kwargs):
		"""Adds a given multiaddr filter to the filter list.

		This will add an address filter to the daemons swarm. Filters applied
		this way will not persist daemon reboots, to achieve that, add your
		filters to the configuration file.

		.. code-block:: python

			>>> client.swarm.filters.add("/ip4/192.168.0.0/ipcidr/16")
			{'Strings': ['/ip4/192.168.0.0/ipcidr/16']}

		Parameters
		----------
		address : str
			Multiaddr to filter

		Returns
		-------
			dict
		
		+---------+-----------------------------+
		| Strings | List of swarm filters added |
		+---------+-----------------------------+
		"""
		args = (address,) + addresses
		return self._client.request('/swarm/filters/add', args, decoder='json', **kwargs)
	
	
	@base.returns_single_item
	def rm(self, address, *addresses, **kwargs):
		"""Removes a given multiaddr filter from the filter list.

		This will remove an address filter from the daemons swarm. Filters
		removed this way will not persist daemon reboots, to achieve that,
		remove your filters from the configuration file.

		.. code-block:: python

			>>> client.swarm.filters.rm("/ip4/192.168.0.0/ipcidr/16")
			{'Strings': ['/ip4/192.168.0.0/ipcidr/16']}

		Parameters
		----------
		address : str
			Multiaddr filter to remove

		Returns
		-------
			dict
		
		+---------+-------------------------------+
		| Strings | List of swarm filters removed |
		+---------+-------------------------------+
		"""
		args = (address,) + addresses
		return self._client.request('/swarm/filters/rm', args, decoder='json', **kwargs)


class Section(base.SectionBase):
	filters = base.SectionProperty(FiltersSection)
	
	
	@base.returns_single_item
	def addrs(self, **kwargs):
		"""Returns the addresses of currently connected peers by peer id.

		.. code-block:: python

			>>> pprint(client.swarm.addrs())
			{'Addrs': {
				'QmNMVHJTSZHTWMWBbmBrQgkA1hZPWYuVJx2DpSGESWW6Kn': [
					'/ip4/10.1.0.1/tcp/4001',
					'/ip4/127.0.0.1/tcp/4001',
					'/ip4/51.254.25.16/tcp/4001',
					'/ip6/2001:41d0:b:587:3cae:6eff:fe40:94d8/tcp/4001',
					'/ip6/2001:470:7812:1045::1/tcp/4001',
					'/ip6/::1/tcp/4001',
					'/ip6/fc02:2735:e595:bb70:8ffc:5293:8af8:c4b7/tcp/4001',
					'/ip6/fd00:7374:6172:100::1/tcp/4001',
					'/ip6/fd20:f8be:a41:0:c495:aff:fe7e:44ee/tcp/4001',
					'/ip6/fd20:f8be:a41::953/tcp/4001'],
				'QmNQsK1Tnhe2Uh2t9s49MJjrz7wgPHj4VyrZzjRe8dj7KQ': [
					'/ip4/10.16.0.5/tcp/4001',
					'/ip4/127.0.0.1/tcp/4001',
					'/ip4/172.17.0.1/tcp/4001',
					'/ip4/178.62.107.36/tcp/4001',
					'/ip6/::1/tcp/4001'],
				…
			}}

		Returns
		-------
			dict
				Multiaddrs of peers by peer id
		
		+-------+-------------------------------------------------------+
		| Addrs | Mapping of PeerIDs to a list its advatised MultiAddrs |
		+-------+-------------------------------------------------------+
		"""
		return self._client.request('/swarm/addrs', decoder='json', **kwargs)
	
	
	@base.returns_single_item
	def connect(self, address, *addresses, **kwargs):
		"""Opens a connection to a given address.

		This will open a new direct connection to a peer address. The address
		format is an IPFS multiaddr::

			/ip4/104.131.131.82/tcp/4001/ipfs/QmaCpDMGvV2BGHeYERUEnRQAwe3N8SzbUtfsmvsqQLuvuJ

		.. code-block:: python

			>>> client.swarm.connect("/ip4/104.131.131.82/tcp/4001/ipfs/Qma … uvuJ")
			{'Strings': ['connect QmaCpDMGvV2BGHeYERUEnRQAwe3 … uvuJ success']}

		Parameters
		----------
		address : str
			Address of peer to connect to

		Returns
		-------
			dict
				Textual connection status report
		"""
		args = (address,) + addresses
		return self._client.request('/swarm/connect', args, decoder='json', **kwargs)
	
	
	@base.returns_single_item
	def disconnect(self, address, *addresses, **kwargs):
		"""Closes the connection to a given address.

		This will close a connection to a peer address. The address format is
		an IPFS multiaddr::

			/ip4/104.131.131.82/tcp/4001/ipfs/QmaCpDMGvV2BGHeYERUEnRQAwe3N8SzbUtfsmvsqQLuvuJ

		The disconnect is not permanent; if IPFS needs to talk to that address
		later, it will reconnect.

		.. code-block:: python

			>>> client.swarm.disconnect("/ip4/104.131.131.82/tcp/4001/ipfs/Qm … uJ")
			{'Strings': ['disconnect QmaCpDMGvV2BGHeYERUEnRQA … uvuJ success']}

		Parameters
		----------
		address : str
			Address of peer to disconnect from

		Returns
		-------
			dict
				Textual connection status report
		"""
		args = (address,) + addresses
		return self._client.request('/swarm/disconnect', args, decoder='json', **kwargs)
	
	
	@base.returns_single_item
	def peers(self, **kwargs):
		"""Returns the addresses & IDs of currently connected peers.

		.. code-block:: python

			>>> client.swarm.peers()
			{'Strings': [
				'/ip4/101.201.40.124/tcp/40001/ipfs/QmZDYAhmMDtnoC6XZ … kPZc',
				'/ip4/104.131.131.82/tcp/4001/ipfs/QmaCpDMGvV2BGHeYER … uvuJ',
				'/ip4/104.223.59.174/tcp/4001/ipfs/QmeWdgoZezpdHz1PX8 … 1jB6',
				…
				'/ip6/fce3: … :f140/tcp/43901/ipfs/QmSoLnSGccFuZQJzRa … ca9z'
			]}

		Returns
		-------
			dict
		
		+---------+----------------------------------------------------+
		| Strings | List of MultiAddrs that the daemon is connected to |
		+---------+----------------------------------------------------+
		"""
		return self._client.request('/swarm/peers', decoder='json', **kwargs)