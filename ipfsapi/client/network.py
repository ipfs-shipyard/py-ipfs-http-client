# -*- coding: utf-8 -*-
from __future__ import absolute_import

import warnings

from .. import exceptions
from . import base


class SubChannel:
	"""
	Wrapper for a pubsub subscription object that allows for easy
	closing of subscriptions.
	"""
	def __init__(self, sub):
		self.__sub = sub

	def read_message(self):
		return next(self.__sub)

	def __iter__(self):
		return self.__sub

	def close(self):
		self.__sub.close()

	def __enter__(self):
		return self

	def __exit__(self, *a):
		self.close()


class BootstrapSection(base.SectionBase):
	def bootstrap(self, **kwargs):
		"""Deprecated method: Please use “client.bootstrap.list” instead"""
		warnings.warn(
			"IPFS API function “bootstrap” has been renamed to “bootstrap.list”",
			FutureWarning
		)

		self.bootstrap_list(**kwargs)


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


	def list(self, **kwargs):
		"""Returns the addresses of peers used during initial discovery of the
		IPFS network.

		Peers are output in the format ``<multiaddr>/<peerID>``.

		.. code-block:: python

			>>> c.bootstrap.list()
			{'Peers': [
				'/ip4/104.131.131.82/tcp/4001/ipfs/QmaCpDMGvV2BGHeYER … uvuJ',
				'/ip4/104.236.176.52/tcp/4001/ipfs/QmSoLnSGccFuZQJzRa … ca9z',
				'/ip4/104.236.179.241/tcp/4001/ipfs/QmSoLPppuBtQSGwKD … KrGM',
				…
				'/ip4/178.62.61.185/tcp/4001/ipfs/QmSoLMeWqB7YGVLJN3p … QBU3']}

		Returns
		-------
			dict : List of known bootstrap peers
		"""
		return self._client.request('/bootstrap', decoder='json', **kwargs)


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



class BitswapSection(base.SectionBase):
	def wantlist(self, peer=None, **kwargs):
		"""Returns blocks currently on the bitswap wantlist.

		.. code-block:: python

			>>> c.bitswap.wantlist()
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
			dict : List of wanted blocks
		"""
		args = (peer,)
		return self._client.request('/bitswap/wantlist', args, decoder='json', **kwargs)


	def stat(self, **kwargs):
		"""Returns some diagnostic information from the bitswap agent.

		.. code-block:: python

			>>> c.bitswap.stat()
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
			dict : Statistics, peers and wanted blocks
		"""
		return self._client.request('/bitswap/stat', decoder='json', **kwargs)


	def unwant(self, key, **kwargs):
		"""
		Remove a given block from wantlist.

		Parameters
		----------
		key : str
			Key to remove from wantlist.
		"""
		args = (key,)
		return self._client.request('/bitswap/unwant', args, **kwargs)



class DHTSection(base.SectionBase):
	def findpeer(self, peer_id, *peer_ids, **kwargs):
		"""Queries the DHT for all of the associated multiaddresses.

		.. code-block:: python

			>>> c.dht_findpeer("QmaxqKpiYNr62uSFBhxJAMmEMkT6dvc3oHkrZN … MTLZ")
			[{'ID': 'QmfVGMFrwW6AV6fTWmD6eocaTybffqAvkVLXQEFrYdk6yc',
			  'Extra': '', 'Type': 6, 'Responses': None},
			 {'ID': 'QmTKiUdjbRjeN9yPhNhG1X38YNuBdjeiV9JXYWzCAJ4mj5',
			  'Extra': '', 'Type': 6, 'Responses': None},
			 {'ID': 'QmTGkgHSsULk8p3AKTAqKixxidZQXFyF7mCURcutPqrwjQ',
			  'Extra': '', 'Type': 6, 'Responses': None},
			 …
			 {'ID': '', 'Extra': '', 'Type': 2,
			  'Responses': [
				{'ID': 'QmaxqKpiYNr62uSFBhxJAMmEMkT6dvc3oHkrZNpH2VMTLZ',
				 'Addrs': [
					'/ip4/10.9.8.1/tcp/4001',
					'/ip6/::1/tcp/4001',
					'/ip4/164.132.197.107/tcp/4001',
					'/ip4/127.0.0.1/tcp/4001']}
			  ]}]

		Parameters
		----------
		peer_id : str
			The ID of the peer to search for

		Returns
		-------
			dict : List of multiaddrs
		"""
		args = (peer_id,) + peer_ids
		return self._client.request('/dht/findpeer', args, decoder='json', **kwargs)


	def findprovs(self, multihash, *multihashes, **kwargs):
		"""Finds peers in the DHT that can provide a specific value.

		.. code-block:: python

			>>> c.dht_findprovs("QmNPXDC6wTXVmZ9Uoc8X1oqxRRJr4f1sDuyQu … mpW2")
			[{'ID': 'QmaxqKpiYNr62uSFBhxJAMmEMkT6dvc3oHkrZNpH2VMTLZ',
			  'Extra': '', 'Type': 6, 'Responses': None},
			 {'ID': 'QmaK6Aj5WXkfnWGoWq7V8pGUYzcHPZp4jKQ5JtmRvSzQGk',
			  'Extra': '', 'Type': 6, 'Responses': None},
			 {'ID': 'QmdUdLu8dNvr4MVW1iWXxKoQrbG6y1vAVWPdkeGK4xppds',
			  'Extra': '', 'Type': 6, 'Responses': None},
			 …
			 {'ID': '', 'Extra': '', 'Type': 4, 'Responses': [
				{'ID': 'QmVgNoP89mzpgEAAqK8owYoDEyB97Mk … E9Uc', 'Addrs': None}
			  ]},
			 {'ID': 'QmaxqKpiYNr62uSFBhxJAMmEMkT6dvc3oHkrZNpH2VMTLZ',
			  'Extra': '', 'Type': 1, 'Responses': [
				{'ID': 'QmSHXfsmN3ZduwFDjeqBn1C8b1tcLkxK6yd … waXw', 'Addrs': [
					'/ip4/127.0.0.1/tcp/4001',
					'/ip4/172.17.0.8/tcp/4001',
					'/ip6/::1/tcp/4001',
					'/ip4/52.32.109.74/tcp/1028'
				  ]}
			  ]}]

		Parameters
		----------
		multihash : str
			The DHT key to find providers for

		Returns
		-------
			dict : List of provider Peer IDs
		"""
		args = (multihash,) + multihashes
		return self._client.request('/dht/findprovs', args, decoder='json', **kwargs)


	def get(self, key, *keys, **kwargs):
		"""Queries the DHT for its best value related to given key.

		There may be several different values for a given key stored in the
		DHT; in this context *best* means the record that is most desirable.
		There is no one metric for *best*: it depends entirely on the key type.
		For IPNS, *best* is the record that is both valid and has the highest
		sequence number (freshest). Different key types may specify other rules
		for what they consider to be the *best*.

		Parameters
		----------
		key : str
			One or more keys whose values should be looked up

		Returns
		-------
			str
		"""
		args = (key,) + keys
		res = self._client.request('/dht/get', args, decoder='json', **kwargs)

		if isinstance(res, dict) and "Extra" in res:
			return res["Extra"]
		else:
			for r in res:
				if "Extra" in r and len(r["Extra"]) > 0:
					return r["Extra"]
		raise exceptions.Error("empty response from DHT")


	#XXX: Implement `provide(cid)`


	def put(self, key, value, **kwargs):
		"""Writes a key/value pair to the DHT.

		Given a key of the form ``/foo/bar`` and a value of any form, this will
		write that value to the DHT with that key.

		Keys have two parts: a keytype (foo) and the key name (bar). IPNS uses
		the ``/ipns/`` keytype, and expects the key name to be a Peer ID. IPNS
		entries are formatted with a special strucutre.

		You may only use keytypes that are supported in your ``ipfs`` binary:
		``go-ipfs`` currently only supports the ``/ipns/`` keytype. Unless you
		have a relatively deep understanding of the key's internal structure,
		you likely want to be using the :meth:`~ipfsapi.Client.name_publish`
		instead.

		Value is arbitrary text.

		.. code-block:: python

			>>> c.dht_put("QmVgNoP89mzpgEAAqK8owYoDEyB97Mkc … E9Uc", "test123")
			[{'ID': 'QmfLy2aqbhU1RqZnGQyqHSovV8tDufLUaPfN1LNtg5CvDZ',
			  'Extra': '', 'Type': 5, 'Responses': None},
			 {'ID': 'QmZ5qTkNvvZ5eFq9T4dcCEK7kX8L7iysYEpvQmij9vokGE',
			  'Extra': '', 'Type': 5, 'Responses': None},
			 {'ID': 'QmYqa6QHCbe6eKiiW6YoThU5yBy8c3eQzpiuW22SgVWSB8',
			  'Extra': '', 'Type': 6, 'Responses': None},
			 …
			 {'ID': 'QmP6TAKVDCziLmx9NV8QGekwtf7ZMuJnmbeHMjcfoZbRMd',
			  'Extra': '', 'Type': 1, 'Responses': []}]

		Parameters
		----------
		key : str
			A unique identifier
		value : str
			Abitrary text to associate with the input (2048 bytes or less)

		Returns
		-------
			list
		"""
		args = (key, value)
		return self._client.request('/dht/put', args, decoder='json', **kwargs)


	def query(self, peer_id, *peer_ids, **kwargs):
		"""Finds the closest Peer IDs to a given Peer ID by querying the DHT.

		.. code-block:: python

			>>> c.dht_query("/ip4/104.131.131.82/tcp/4001/ipfs/QmaCpDM … uvuJ")
			[{'ID': 'QmPkFbxAQ7DeKD5VGSh9HQrdS574pyNzDmxJeGrRJxoucF',
			  'Extra': '', 'Type': 2, 'Responses': None},
			 {'ID': 'QmR1MhHVLJSLt9ZthsNNhudb1ny1WdhY4FPW21ZYFWec4f',
			  'Extra': '', 'Type': 2, 'Responses': None},
			 {'ID': 'Qmcwx1K5aVme45ab6NYWb52K2TFBeABgCLccC7ntUeDsAs',
			  'Extra': '', 'Type': 2, 'Responses': None},
			 …
			 {'ID': 'QmYYy8L3YD1nsF4xtt4xmsc14yqvAAnKksjo3F3iZs5jPv',
			  'Extra': '', 'Type': 1, 'Responses': []}]

		Parameters
		----------
		peer_id : str
			The peerID to run the query against

		Returns
		-------
			dict : List of peers IDs
		"""
		args = (peer_id,) + peer_ids
		return self._client.request('/dht/query', args, decoder='json', **kwargs)


class PubsubBase(base.SectionBase):
	def ls(self, **kwargs):
		"""Lists subscribed topics by name

		This method returns data that contains a list of
		all topics the user is subscribed to. In order
		to subscribe to a topic ``pubsub.sub`` must be called.

		.. code-block:: python

			# subscribe to a channel
			>>> with c.pubsub.sub("hello") as sub:
			...     c.pubsub.ls()
			{
				'Strings' : ["hello"]
			}

		Returns
		-------
			dict : Dictionary with the key "Strings" who's value is an array of
				   topics we are subscribed to
		"""
		return self._client.request('/pubsub/ls', decoder='json', **kwargs)


	def peers(self, topic=None, **kwargs):
		"""List the peers we are pubsubbing with.

		Lists the id's of other IPFS users who we
		are connected to via some topic. Without specifying
		a topic, IPFS peers from all subscribed topics
		will be returned in the data. If a topic is specified
		only the IPFS id's of the peers from the specified
		topic will be returned in the data.

		.. code-block:: python

			>>> c.pubsub.peers()
			{'Strings':
					[
						'QmPbZ3SDgmTNEB1gNSE9DEf4xT8eag3AFn5uo7X39TbZM8',
						'QmQKiXYzoFpiGZ93DaFBFDMDWDJCRjXDARu4wne2PRtSgA',
						...
						'QmepgFW7BHEtU4pZJdxaNiv75mKLLRQnPi1KaaXmQN4V1a'
					]
			}

			## with a topic

			# subscribe to a channel
			>>> with c.pubsub.sub('hello') as sub:
			...     c.pubsub.peers(topic='hello')
			{'String':
					[
						'QmPbZ3SDgmTNEB1gNSE9DEf4xT8eag3AFn5uo7X39TbZM8',
						...
						# other peers connected to the same channel
					]
			}

		Parameters
		----------
		topic : str
			The topic to list connected peers of
			(defaults to None which lists peers for all topics)

		Returns
		-------
			dict : Dictionary with the ke "Strings" who's value is id of IPFS
				   peers we're pubsubbing with
		"""
		args = (topic,) if topic is not None else ()
		return self._client.request('/pubsub/peers', args, decoder='json', **kwargs)


	def publish(self, topic, payload, **kwargs):
		"""Publish a message to a given pubsub topic

		Publishing will publish the given payload (string) to
		everyone currently subscribed to the given topic.

		All data (including the id of the publisher) is automatically
		base64 encoded when published.

		.. code-block:: python

			# publishes the message 'message' to the topic 'hello'
			>>> c.pubsub.publish('hello', 'message')
			[]

		Parameters
		----------
		topic : str
			Topic to publish to
		payload : Data to be published to the given topic

		Returns
		-------
			list : empty list
		"""
		args = (topic, payload)
		return self._client.request('/pubsub/pub', args, decoder='json', **kwargs)


	def subscribe(self, topic, discover=False, **kwargs):
		"""Subscribe to mesages on a given topic

		Subscribing to a topic in IPFS means anytime
		a message is published to a topic, the subscribers
		will be notified of the publication.

		The connection with the pubsub topic is opened and read.
		The Subscription returned should be used inside a context
		manager to ensure that it is closed properly and not left
		hanging.

		.. code-block:: python

			>>> sub = c.pubsub.subscribe('testing')
			>>> with c.pubsub.subscribe('testing') as sub:
			# publish a message 'hello' to the topic 'testing'
			... c.pubsub.publish('testing', 'hello')
			... for message in sub:
			...     print(message)
			...     # Stop reading the subscription after
			...     # we receive one publication
			...     break
			{'from': '<base64encoded IPFS id>',
			 'data': 'aGVsbG8=',
			 'topicIDs': ['testing']}

			# NOTE: in order to receive published data
			# you must already be subscribed to the topic at publication
			# time.

		Parameters
		----------
		topic : str
			Name of a topic to subscribe to

		discover : bool
			Try to discover other peers subscibed to the same topic
			(defaults to False)

		Returns
		-------
			Generator wrapped in a context
			manager that maintains a connection
			stream to the given topic.
		"""
		args = (topic, discover)
		return SubChannel(self._client.request('/pubsub/sub', args, stream=True, decoder='json'))



class SwarmFiltersSection(base.SectionBase):
	def add(self, address, *addresses, **kwargs):
		"""Adds a given multiaddr filter to the filter list.

		This will add an address filter to the daemons swarm. Filters applied
		this way will not persist daemon reboots, to achieve that, add your
		filters to the configuration file.

		.. code-block:: python

			>>> c.swarm.filters.add("/ip4/192.168.0.0/ipcidr/16")
			{'Strings': ['/ip4/192.168.0.0/ipcidr/16']}

		Parameters
		----------
		address : str
			Multiaddr to filter

		Returns
		-------
			dict : List of swarm filters added
		"""
		args = (address,) + addresses
		return self._client.request('/swarm/filters/add', args, decoder='json', **kwargs)


	def rm(self, address, *addresses, **kwargs):
		"""Removes a given multiaddr filter from the filter list.

		This will remove an address filter from the daemons swarm. Filters
		removed this way will not persist daemon reboots, to achieve that,
		remove your filters from the configuration file.

		.. code-block:: python

			>>> c.swarm.filters.rm("/ip4/192.168.0.0/ipcidr/16")
			{'Strings': ['/ip4/192.168.0.0/ipcidr/16']}

		Parameters
		----------
		address : str
			Multiaddr filter to remove

		Returns
		-------
			dict : List of swarm filters removed
		"""
		args = (address,) + addresses
		return self._client.request('/swarm/filters/rm', args, decoder='json', **kwargs)


class SwarmSection(base.SectionBase):
	filters = base.SectionProperty(SwarmFiltersSection)


	def addrs(self, **kwargs):
		"""Returns the addresses of currently connected peers by peer id.

		.. code-block:: python

			>>> pprint(c.swarm.addrs())
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
			dict : Multiaddrs of peers by peer id
		"""
		return self._client.request('/swarm/addrs', decoder='json', **kwargs)


	def connect(self, address, *addresses, **kwargs):
		"""Opens a connection to a given address.

		This will open a new direct connection to a peer address. The address
		format is an IPFS multiaddr::

			/ip4/104.131.131.82/tcp/4001/ipfs/QmaCpDMGvV2BGHeYERUEnRQAwe3N8SzbUtfsmvsqQLuvuJ

		.. code-block:: python

			>>> c.swarm.connect("/ip4/104.131.131.82/tcp/4001/ipfs/Qma … uvuJ")
			{'Strings': ['connect QmaCpDMGvV2BGHeYERUEnRQAwe3 … uvuJ success']}

		Parameters
		----------
		address : str
			Address of peer to connect to

		Returns
		-------
			dict : Textual connection status report
		"""
		args = (address,) + addresses
		return self._client.request('/swarm/connect', args, decoder='json', **kwargs)


	def disconnect(self, address, *addresses, **kwargs):
		"""Closes the connection to a given address.

		This will close a connection to a peer address. The address format is
		an IPFS multiaddr::

			/ip4/104.131.131.82/tcp/4001/ipfs/QmaCpDMGvV2BGHeYERUEnRQAwe3N8SzbUtfsmvsqQLuvuJ

		The disconnect is not permanent; if IPFS needs to talk to that address
		later, it will reconnect.

		.. code-block:: python

			>>> c.swarm.disconnect("/ip4/104.131.131.82/tcp/4001/ipfs/Qm … uJ")
			{'Strings': ['disconnect QmaCpDMGvV2BGHeYERUEnRQA … uvuJ success']}

		Parameters
		----------
		address : str
			Address of peer to disconnect from

		Returns
		-------
			dict : Textual connection status report
		"""
		args = (address,) + addresses
		return self._client.request('/swarm/disconnect', args, decoder='json', **kwargs)


	def peers(self, **kwargs):
		"""Returns the addresses & IDs of currently connected peers.

		.. code-block:: python

			>>> c.swarm.peers()
			{'Strings': [
				'/ip4/101.201.40.124/tcp/40001/ipfs/QmZDYAhmMDtnoC6XZ … kPZc',
				'/ip4/104.131.131.82/tcp/4001/ipfs/QmaCpDMGvV2BGHeYER … uvuJ',
				'/ip4/104.223.59.174/tcp/4001/ipfs/QmeWdgoZezpdHz1PX8 … 1jB6',
				…
				'/ip6/fce3: … :f140/tcp/43901/ipfs/QmSoLnSGccFuZQJzRa … ca9z']}

		Returns
		-------
			dict : List of multiaddrs of currently connected peers
		"""
		return self._client.request('/swarm/peers', decoder='json', **kwargs)


class NameSection(base.SectionBase):
	def publish(self, ipfs_path, resolve=True, lifetime="24h", ttl=None, key=None, **kwargs):
		"""Publishes an object to IPNS.

		IPNS is a PKI namespace, where names are the hashes of public keys, and
		the private key enables publishing new (signed) values. In publish, the
		default value of *name* is your own identity public key.

		.. code-block:: python

			>>> c.name.publish('/ipfs/QmfZY61ukoQuCX8e5Pt7v8pRfhkyxwZK … GZ5d')
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
		ttl : int
			Time duration this record should be cached for
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
		kwargs.setdefault("opts", opts)

		args = (ipfs_path,)
		return self._client.request('/name/publish', args, decoder='json', **kwargs)


	def resolve(self, name=None, recursive=False, nocache=False, **kwargs):
		"""Gets the value currently published at an IPNS name.

		IPNS is a PKI namespace, where names are the hashes of public keys, and
		the private key enables publishing new (signed) values. In resolve, the
		default value of ``name`` is your own identity public key.

		.. code-block:: python

			>>> c.name.resolve()
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
		kwargs.setdefault("opts", {"recursive": recursive,
								   "nocache": nocache})
		args = (name,) if name is not None else ()
		return self._client.request('/name/resolve', args, decoder='json', **kwargs)


class NetworkBase(base.ClientBase):
	bootstrap = base.SectionProperty(BootstrapSection)
	bitswap   = base.SectionProperty(BitswapSection)
	dht       = base.SectionProperty(DHTSection)
	pubsub    = base.SectionProperty(PubsubBase)
	swarm     = base.SectionProperty(SwarmSection)
	name      = base.SectionProperty(NameSection)

	# Aliases for previous method names
	bootstrap_add  = base.DeprecatedMethodProperty("bootstrap", "add")
	bootstrap_list = base.DeprecatedMethodProperty("bootstrap", "list")
	bootstrap_rm   = base.DeprecatedMethodProperty("bootstrap", "rm")

	bitswap_stat     = base.DeprecatedMethodProperty("bitswap", "stat")
	bitswap_wantlist = base.DeprecatedMethodProperty("bitswap", "wantlist")
	bitswap_unwant   = base.DeprecatedMethodProperty("bitswap", "unwant")

	dht_findpeer  = base.DeprecatedMethodProperty("dht", "findpeer")
	dht_findprovs = base.DeprecatedMethodProperty("dht", "findproves")
	dht_get       = base.DeprecatedMethodProperty("dht", "get")
	dht_put       = base.DeprecatedMethodProperty("dht", "put")
	dht_query     = base.DeprecatedMethodProperty("dht", "query")

	pubsub_ls    = base.DeprecatedMethodProperty("pubsub", "ls")
	pubsub_peers = base.DeprecatedMethodProperty("pubsub", "peers")
	pubsub_pub   = base.DeprecatedMethodProperty("pubsub", "publish")
	pubsub_sub   = base.DeprecatedMethodProperty("pubsub", "subscribe")

	swarm_addrs      = base.DeprecatedMethodProperty("swarm", "addrs")
	swarm_connect    = base.DeprecatedMethodProperty("swarm", "connect")
	swarm_disconnect = base.DeprecatedMethodProperty("swarm", "disconnect")
	swarm_peers      = base.DeprecatedMethodProperty("swarm", "peers")
	swarm_filters_add = base.DeprecatedMethodProperty("swarm", "filters", "add")
	swarm_filters_rm  = base.DeprecatedMethodProperty("swarm", "filters", "rm")

	name_publish = base.DeprecatedMethodProperty("name", "publish")
	name_resolve = base.DeprecatedMethodProperty("name", "resolve")


	def resolve(self, name, recursive=False, **kwargs):
		"""Accepts an identifier and resolves it to the referenced item.

		There are a number of mutable name protocols that can link among
		themselves and into IPNS. For example IPNS references can (currently)
		point at an IPFS object, and DNS links can point at other DNS links,
		IPNS entries, or IPFS objects. This command accepts any of these
		identifiers.

		.. code-block:: python

			>>> c.resolve("/ipfs/QmTkzDwWqPbnAh5YiV5VwcTLnGdw … ca7D/Makefile")
			{'Path': '/ipfs/Qmd2xkBfEwEs9oMTk77A6jrsgurpF3ugXSg7dtPNFkcNMV'}
			>>> c.resolve("/ipns/ipfs.io")
			{'Path': '/ipfs/QmTzQ1JRkWErjk39mryYw2WVaphAZNAREyMchXzYQ7c15n'}

		Parameters
		----------
		name : str
			The name to resolve
		recursive : bool
			Resolve until the result is an IPFS name

		Returns
		-------
			dict : IPFS path of resource
		"""
		kwargs.setdefault("opts", {"recursive": recursive})

		args = (name,)
		return self._client.request('/resolve', args, decoder='json', **kwargs)
