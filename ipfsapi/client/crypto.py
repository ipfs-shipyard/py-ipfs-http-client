# -*- coding: utf-8 -*-
from __future__ import absolute_import

from . import base


class SectionKey(base.SectionBase):
	#XXX: Add `export(name, password)`


	def gen(self, key_name, type, size=2048, **kwargs):
		"""Adds a new public key that can be used for
		:meth:`~ipfsapi.Client.name.publish`.

		.. code-block:: python

			>>> c.key.gen('example_key_name')
			{'Name': 'example_key_name',
			 'Id': 'QmQLaT5ZrCfSkXTH6rUKtVidcxj8jrW3X2h75Lug1AV7g8'}

		Parameters
		----------
		key_name : str
			Name of the new Key to be generated. Used to reference the Keys.
		type : str
			Type of key to generate. The current possible keys types are:

			 * ``"rsa"``
			 * ``"ed25519"``
		size : int
			Bitsize of key to generate

		Returns
		-------
			dict : Key name and Key Id
		"""

		opts = {"type": type, "size": size}
		kwargs.setdefault("opts", opts)
		args = (key_name,)

		return self._client.request('/key/gen', args, decoder='json', **kwargs)


	#XXX: Add `import(name, pam, password)`


	def list(self, **kwargs):
		"""Returns a list of generated public keys that can be used with
		:meth:`~ipfsapi.Client.name.publish`.

		.. code-block:: python

			>>> c.key.list()
			[{'Name': 'self',
			  'Id': 'QmQf22bZar3WKmojipms22PkXH1MZGmvsqzQtuSvQE3uhm'},
			 {'Name': 'example_key_name',
			  'Id': 'QmQLaT5ZrCfSkXTH6rUKtVidcxj8jrW3X2h75Lug1AV7g8'}
			]

		Returns
		-------
			list : List of dictionaries with Names and Ids of public keys.
		"""
		return self._client.request('/key/list', decoder='json', **kwargs)


	def rename(self, key_name, new_key_name, **kwargs):
		"""Rename a keypair

		.. code-block:: python

			>>> c.key.rename("bla", "personal")
			{"Was": "bla",
			 "Now": "personal",
			 "Id": "QmeyrRNxXaasZaoDXcCZgryoBCga9shaHQ4suHAYXbNZF3",
			 "Overwrite": False}

		Parameters
		----------
		key_name : str
			Current name of the key to rename
		new_key_name : str
			New name of the key

		Returns
		-------
			dict : List of key names and IDs that have been removed
		"""
		args = (key_name, new_key_name)
		return self._client.request(
			'/key/rename', args, decoder='json', **kwargs
		)


	def rm(self, key_name, *key_names, **kwargs):
		"""Remove a keypair

		.. code-block:: python

			>>> c.key_rm("bla")
			{"Keys": [
				{"Name": "bla",
				 "Id": "QmfJpR6paB6h891y7SYXGe6gapyNgepBeAYMbyejWA4FWA"}
			]}

		Parameters
		----------
		key_name : str
			Name of the key(s) to remove.

		Returns
		-------
			dict : List of key names and IDs that have been removed
		"""
		args = (key_name,) + key_names
		return self._client.request('/key/rm', args, decoder='json', **kwargs)


class CryptoBase(base.ClientBase):
	key = base.SectionProperty(SectionKey)

	# Aliases for previous method names
	key_gen    = base.DeprecatedMethodProperty("key", "gen")
	key_list   = base.DeprecatedMethodProperty("key", "list")
	key_rename = base.DeprecatedMethodProperty("key", "rename")
	key_rm     = base.DeprecatedMethodProperty("key", "rm")