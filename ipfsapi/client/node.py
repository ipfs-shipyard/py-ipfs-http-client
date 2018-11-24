# -*- coding: utf-8 -*-
from __future__ import absolute_import

from .. import exceptions
from . import base


class RepoSection(base.SectionBase):
	def gc(self, **kwargs):
		"""Removes stored objects that are not pinned from the repo.

		.. code-block:: python

			>>> c.repo.gc()
			[{'Key': 'QmNPXDC6wTXVmZ9Uoc8X1oqxRRJr4f1sDuyQuwaHG2mpW2'},
			 {'Key': 'QmNtXbF3AjAk59gQKRgEdVabHcSsiPUnJwHnZKyj2x8Z3k'},
			 {'Key': 'QmRVBnxUCsD57ic5FksKYadtyUbMsyo9KYQKKELajqAp4q'},
			 …
			 {'Key': 'QmYp4TeCurXrhsxnzt5wqLqqUz8ZRg5zsc7GuUrUSDtwzP'}]

		Performs a garbage collection sweep of the local set of
		stored objects and remove ones that are not pinned in order
		to reclaim hard disk space. Returns the hashes of all collected
		objects.

		Returns
		-------
			dict : List of IPFS objects that have been removed
		"""
		return self._client.request('/repo/gc', decoder='json', **kwargs)


	def stat(self, **kwargs):
		"""Displays the repo's status.

		Returns the number of objects in the repo and the repo's size,
		version, and path.

		.. code-block:: python

			>>> c.repo.stat()
			{'NumObjects': 354,
			 'RepoPath': '…/.local/share/ipfs',
			 'Version': 'fs-repo@4',
			 'RepoSize': 13789310}

		Returns
		-------
			dict : General information about the IPFS file repository

		+------------+-------------------------------------------------+
		| NumObjects | Number of objects in the local repo.            |
		+------------+-------------------------------------------------+
		| RepoPath   | The path to the repo being currently used.      |
		+------------+-------------------------------------------------+
		| RepoSize   | Size in bytes that the repo is currently using. |
		+------------+-------------------------------------------------+
		| Version    | The repo version.                               |
		+------------+-------------------------------------------------+
		"""
		return self._client.request('/repo/stat', decoder='json', **kwargs)


	#XXX: `version()`


class ConfigSection(base.SectionBase):
	__call__ = base.DeprecatedMethodProperty("set", prefix=["config"], strip=1)


	def get(self, **kwargs):
		#XXX: Support the optional `key` parameter
		"""Returns the current used server configuration.

		.. warning::

			The configuration file contains private key data that must be
			handled with care.

		.. code-block:: python

			>>> config = c.config.get()
			>>> config['Addresses']
			{'API': '/ip4/127.0.0.1/tcp/5001',
			 'Gateway': '/ip4/127.0.0.1/tcp/8080',
			 'Swarm': ['/ip4/0.0.0.0/tcp/4001', '/ip6/::/tcp/4001']},
			>>> config['Discovery']
			{'MDNS': {'Enabled': True, 'Interval': 10}}

		Returns
		-------
			dict : The entire IPFS daemon configuration
		"""
		return self._client.request('/config/show', decoder='json', **kwargs)


	def replace(self, config, **kwargs):
		"""Replaces the existing config with a user-defined config.

		Make sure to back up the config file first if neccessary, as this
		operation can't be undone.
		"""
		return self._client.request('/config/replace', (config,), decoder='json', **kwargs)


	def set(self, key, value=None, **kwargs):
		"""Add or replace a configuration value.

		.. code-block:: python

			>>> c.config("Addresses.Gateway")
			{'Key': 'Addresses.Gateway', 'Value': '/ip4/127.0.0.1/tcp/8080'}
			>>> c.config("Addresses.Gateway", "/ip4/127.0.0.1/tcp/8081")
			{'Key': 'Addresses.Gateway', 'Value': '/ip4/127.0.0.1/tcp/8081'}

		Parameters
		----------
		key : str
			The key of the configuration entry (e.g. "Addresses.API")
		value : dict
			The value to set the configuration entry to

		Returns
		-------
			dict : Requested/updated key and its (new) value
		"""
		args = (key, value)
		return self._client.request('/config', args, decoder='json', **kwargs)


class LogSection(base.SectionBase):
	def level(self, subsystem, level, **kwargs):
		r"""Changes the logging output of a running daemon.

		.. code-block:: python

			>>> c.log_level("path", "info")
			{'Message': "Changed log level of 'path' to 'info'\n"}

		Parameters
		----------
		subsystem : str
			The subsystem logging identifier (Use ``"all"`` for all subsystems)
		level : str
			The desired logging level. Must be one of:

			 * ``"debug"``
			 * ``"info"``
			 * ``"warning"``
			 * ``"error"``
			 * ``"fatal"``
			 * ``"panic"``

		Returns
		-------
			dict : Status message
		"""
		args = (subsystem, level)
		return self._client.request('/log/level', args,
		                            decoder='json', **kwargs)

	def ls(self, **kwargs):
		"""Lists the logging subsystems of a running daemon.

		.. code-block:: python

			>>> c.log_ls()
			{'Strings': [
				'github.com/ipfs/go-libp2p/p2p/host', 'net/identify',
				'merkledag', 'providers', 'routing/record', 'chunk', 'mfs',
				'ipns-repub', 'flatfs', 'ping', 'mockrouter', 'dagio',
				'cmds/files', 'blockset', 'engine', 'mocknet', 'config',
				'commands/http', 'cmd/ipfs', 'command', 'conn', 'gc',
				'peerstore', 'core', 'coreunix', 'fsrepo', 'core/server',
				'boguskey', 'github.com/ipfs/go-libp2p/p2p/host/routed',
				'diagnostics', 'namesys', 'fuse/ipfs', 'node', 'secio',
				'core/commands', 'supernode', 'mdns', 'path', 'table',
				'swarm2', 'peerqueue', 'mount', 'fuse/ipns', 'blockstore',
				'github.com/ipfs/go-libp2p/p2p/host/basic', 'lock', 'nat',
				'importer', 'corerepo', 'dht.pb', 'pin', 'bitswap_network',
				'github.com/ipfs/go-libp2p/p2p/protocol/relay', 'peer',
				'transport', 'dht', 'offlinerouting', 'tarfmt', 'eventlog',
				'ipfsaddr', 'github.com/ipfs/go-libp2p/p2p/net/swarm/addr',
				'bitswap', 'reprovider', 'supernode/proxy', 'crypto', 'tour',
				'commands/cli', 'blockservice']}

		Returns
		-------
			dict : List of daemon logging subsystems
		"""
		return self._client.request('/log/ls', decoder='json', **kwargs)

	def tail(self, **kwargs):
		r"""Reads log outputs as they are written.

		This function returns an iterator needs to be closed using a context
		manager (``with``-statement) or using the ``.close()`` method.

		.. code-block:: python

			>>> with c.log_tail() as log_tail_iter:
			...     for item in log_tail_iter:
			...         print(item)
			...
			{"event":"updatePeer","system":"dht",
			 "peerID":"QmepsDPxWtLDuKvEoafkpJxGij4kMax11uTH7WnKqD25Dq",
			 "session":"7770b5e0-25ec-47cd-aa64-f42e65a10023",
			 "time":"2016-08-22T13:25:27.43353297Z"}
			{"event":"handleAddProviderBegin","system":"dht",
			 "peer":"QmepsDPxWtLDuKvEoafkpJxGij4kMax11uTH7WnKqD25Dq",
			 "session":"7770b5e0-25ec-47cd-aa64-f42e65a10023",
			 "time":"2016-08-22T13:25:27.433642581Z"}
			{"event":"handleAddProvider","system":"dht","duration":91704,
			 "key":"QmNT9Tejg6t57Vs8XM2TVJXCwevWiGsZh3kB4HQXUZRK1o",
			 "peer":"QmepsDPxWtLDuKvEoafkpJxGij4kMax11uTH7WnKqD25Dq",
			 "session":"7770b5e0-25ec-47cd-aa64-f42e65a10023",
			 "time":"2016-08-22T13:25:27.433747513Z"}
			{"event":"updatePeer","system":"dht",
			 "peerID":"QmepsDPxWtLDuKvEoafkpJxGij4kMax11uTH7WnKqD25Dq",
			 "session":"7770b5e0-25ec-47cd-aa64-f42e65a10023",
			 "time":"2016-08-22T13:25:27.435843012Z"}
			…

		Returns
		-------
			iterable
		"""
		return self._client.request('/log/tail', decoder='json',
		                            stream=True, **kwargs)


class NodeBase(base.ClientBase):
	config = base.SectionProperty(ConfigSection)
	log    = base.SectionProperty(LogSection)
	repo   = base.SectionProperty(RepoSection)
	#XXX: stats.*

	# Aliases for previous method names
	repo_gc   = base.DeprecatedMethodProperty("repo", "gc")
	repo_stat = base.DeprecatedMethodProperty("repo", "stat")

	config_show    = base.DeprecatedMethodProperty("config", "get")
	config_replace = base.DeprecatedMethodProperty("config", "replace")

	log_level = base.DeprecatedMethodProperty("log", "level")
	log_ls    = base.DeprecatedMethodProperty("log", "ls")
	log_tail  = base.DeprecatedMethodProperty("log", "tail")



	def id(self, peer=None, **kwargs):
		"""Shows IPFS Node ID info.

		Returns the PublicKey, ProtocolVersion, ID, AgentVersion and
		Addresses of the connected daemon or some other node.

		.. code-block:: python

			>>> c.id()
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
			dict : Information about the IPFS node
		"""
		args = (peer,) if peer is not None else ()
		return self._client.request('/id', args, decoder='json', **kwargs)


	#XXX: isOnline()


	def ping(self, peer, *peers, **kwargs):
		"""Provides round-trip latency information for the routing system.

		Finds nodes via the routing system, sends pings, waits for pongs,
		and prints out round-trip latency information.

		.. code-block:: python

			>>> c.ping("QmTzQ1JRkWErjk39mryYw2WVaphAZNAREyMchXzYQ7c15n")
			[{'Success': True,  'Time': 0,
			  'Text': 'Looking up peer QmTzQ1JRkWErjk39mryYw2WVaphAZN … c15n'},
			 {'Success': False, 'Time': 0,
			  'Text': 'Peer lookup error: routing: not found'}]

		Parameters
		----------
		peer : str
			ID of peer to be pinged
		count : int
			Number of ping messages to send (Default: ``10``)

		Returns
		-------
			list : Progress reports from the ping
		"""
		#PY2: No support for kw-only parameters after glob parameters
		if "count" in kwargs:
			kwargs.setdefault("opts", {"count": kwargs["count"]})
			del kwargs["count"]

		args = (peer,) + peers
		return self._client.request('/ping', args, decoder='json', **kwargs)


	def stop(self):
		"""Stop the connected IPFS daemon instance.

		Sending any further requests after this will fail with
		``ipfsapi.exceptions.ConnectionError``, until you start another IPFS
		daemon instance.
		"""
		try:
			return self._client.request('/shutdown')
		except exceptions.ConnectionError:
			# Sometimes the daemon kills the connection before sending a
			# response causing an incorrect `ConnectionError` to bubble
			pass
	shutdown = base.DeprecatedMethodProperty("stop")


	def version(self, **kwargs):
		"""Returns the software version of the currently connected node.

		.. code-block:: python

			>>> c.version()
			{'Version': '0.4.3-rc2', 'Repo': '4', 'Commit': '',
			 'System': 'amd64/linux', 'Golang': 'go1.6.2'}

		Returns
		-------
			dict : Daemon and system version information
		"""
		return self._client.request('/version', decoder='json', **kwargs)