# -*- coding: utf-8 -*-
from __future__ import absolute_import

from . import base

from .. import exceptions


class Base(base.ClientBase):
	@base.returns_single_item
	def dns(self, domain_name, recursive=False, **kwargs):
		"""Resolves DNS links to the referenced object.

		CIDs are hard to remember, but domain names are usually easy to
		remember. To create memorable aliases for CIDs, DNS TXT records
		can point to other DNS links, IPFS objects, IPNS keys, etc.
		This command resolves those links to the referenced object.

		For example, with this DNS TXT record::

			>>> import dns.resolver
			>>> a = dns.resolver.query("ipfs.io", "TXT")
			>>> a.response.answer[0].items[0].to_text()
			'"dnslink=/ipfs/QmTzQ1JRkWErjk39mryYw2WVaphAZNAREyMchXzYQ7c15n"'

		The resolver will give::

			>>> client.dns("ipfs.io")
			{'Path': '/ipfs/QmTzQ1JRkWErjk39mryYw2WVaphAZNAREyMchXzYQ7c15n'}

		Parameters
		----------
		domain_name : str
			The domain-name name to resolve
		recursive : bool
			Resolve until the name is not a DNS link

		Returns
		-------
			dict
		
		+------+-------------------------------------+
		| Path | Resource were a DNS entry points to |
		+------+-------------------------------------+
		"""
		kwargs.setdefault("opts", {})["recursive"] = recursive

		args = (domain_name,)
		return self._client.request('/dns', args, decoder='json', **kwargs)
	
	
	@base.returns_single_item
	def id(self, peer=None, **kwargs):
		"""Shows IPFS Node ID info.

		Returns the PublicKey, ProtocolVersion, ID, AgentVersion and
		Addresses of the connected daemon or some other node.

		.. code-block:: python

			>>> client.id()
			{'ID': 'QmVgNoP89mzpgEAAqK8owYoDEyB97MkcGvoWZir8otE9Uc',
			'PublicKey': 'CAASpgIwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggE … BAAE=',
			'AgentVersion': 'go-libp2p/3.3.4',
			'ProtocolVersion': 'ipfs/0.1.0',
			'Addresses': [
				'/ip4/127.0.0.1/tcp/4001/ipfs/QmVgNoP89mzpgEAAqK8owYo … E9Uc',
				'/ip4/10.1.0.172/tcp/4001/ipfs/QmVgNoP89mzpgEAAqK8owY … E9Uc',
				'/ip4/172.18.0.1/tcp/4001/ipfs/QmVgNoP89mzpgEAAqK8owY … E9Uc',
				'/ip6/::1/tcp/4001/ipfs/QmVgNoP89mzpgEAAqK8owYoDEyB97 … E9Uc',
				'/ip6/fccc:7904:b05b:a579:957b:deef:f066:cad9/tcp/400 … E9Uc',
				'/ip6/fd56:1966:efd8::212/tcp/4001/ipfs/QmVgNoP89mzpg … E9Uc',
				'/ip6/fd56:1966:efd8:0:def1:34d0:773:48f/tcp/4001/ipf … E9Uc',
				'/ip6/2001:db8:1::1/tcp/4001/ipfs/QmVgNoP89mzpgEAAqK8 … E9Uc',
				'/ip4/77.116.233.54/tcp/4001/ipfs/QmVgNoP89mzpgEAAqK8 … E9Uc',
				'/ip4/77.116.233.54/tcp/10842/ipfs/QmVgNoP89mzpgEAAqK … E9Uc']}

		Parameters
		----------
		peer : str
			Peer.ID of the node to look up (local node if ``None``)

		Returns
		-------
			dict
				Information about the IPFS node
		"""
		args = (peer,) if peer is not None else ()
		return self._client.request('/id', args, decoder='json', **kwargs)


	#TODO: isOnline()
	
	
	def ping(self, peer, *peers, **kwargs):
		"""Provides round-trip latency information for the routing system.
		
		Finds nodes via the routing system, sends pings, waits for pongs,
		and prints out round-trip latency information.
		
		.. code-block:: python
			
			>>> client.ping("QmTzQ1JRkWErjk39mryYw2WVaphAZNAREyMchXzYQ7c15n")
			[{'Success': True,  'Time': 0,
			  'Text': 'Looking up peer QmTzQ1JRkWErjk39mryYw2WVaphAZN … c15n'},
			 {'Success': False, 'Time': 0,
			  'Text': 'Peer lookup error: routing: not found'}]
		
		.. hint::
			
			Pass ``stream=True`` to receive ping progress reports as they
			arrive.
		
		Parameters
		----------
		peer : str
			ID of peer to be pinged
		count : int
			Number of ping messages to send (Default: ``10``)
		
		Returns
		-------
			list
				Progress reports from the ping
		"""
		#PY2: No support for kw-only parameters after glob parameters
		if "count" in kwargs:
			kwargs.setdefault("opts", {})["count"] = kwargs["count"]
			del kwargs["count"]
		
		args = (peer,) + peers
		return self._client.request('/ping', args, decoder='json', **kwargs)
	
	
	@base.returns_single_item
	def resolve(self, name, recursive=False, **kwargs):
		"""Accepts an identifier and resolves it to the referenced item.
		
		There are a number of mutable name protocols that can link among
		themselves and into IPNS. For example IPNS references can (currently)
		point at an IPFS object, and DNS links can point at other DNS links,
		IPNS entries, or IPFS objects. This command accepts any of these
		identifiers.
		
		.. code-block:: python
			
			>>> client.resolve("/ipfs/QmTkzDwWqPbnAh5YiV5VwcTLnGdw … ca7D/Makefile")
			{'Path': '/ipfs/Qmd2xkBfEwEs9oMTk77A6jrsgurpF3ugXSg7dtPNFkcNMV'}
			>>> client.resolve("/ipns/ipfs.io")
			{'Path': '/ipfs/QmTzQ1JRkWErjk39mryYw2WVaphAZNAREyMchXzYQ7c15n'}
		
		Parameters
		----------
		name : str
			The name to resolve
		recursive : bool
			Resolve until the result is an IPFS name

		Returns
		-------
			dict
		
		+------+-------------------------------------+
		| Path | IPFS path of the requested resource |
		+------+-------------------------------------+
		"""
		kwargs.setdefault("opts", {})["recursive"] = recursive
		
		args = (name,)
		return self._client.request('/resolve', args, decoder='json', **kwargs)
	
	
	@base.returns_no_item
	def stop(self):
		"""Stop the connected IPFS daemon instance.
		
		Sending any further requests after this will fail with
		:class:`~ipfshttpclient.exceptions.ConnectionError`, until you start
		another IPFS daemon instance.
		"""
		try:
			return self._client.request('/shutdown')
		except exceptions.ConnectionError:
			# Sometimes the daemon kills the connection before sending a
			# response causing an incorrect `ConnectionError` to bubble
			pass
	
	
	@base.returns_single_item
	def version(self, **kwargs):
		"""Returns the software version of the currently connected node.
		
		.. code-block:: python
			
			>>> client.version()
			{'Version': '0.4.3-rc2', 'Repo': '4', 'Commit': '',
			 'System': 'amd64/linux', 'Golang': 'go1.6.2'}
		
		Returns
		-------
			dict
				Daemon and system version information
		"""
		return self._client.request('/version', decoder='json', **kwargs)