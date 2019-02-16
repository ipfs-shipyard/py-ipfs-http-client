# -*- coding: utf-8 -*-
from __future__ import absolute_import

from . import base


class Section(base.SectionBase):
	#TODO: Add `export(name, password)`
	
	
	@base.returns_single_item
	def gen(self, key_name, type, size=2048, **kwargs):
		"""Adds a new public key that can be used for
		:meth:`~ipfshttpclient.Client.name.publish`.

		.. code-block:: python

			>>> client.key.gen('example_key_name')
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
			dict
		
		+------+---------------------------------------------------+
		| Name | The name of the newly generated key               |
		+------+---------------------------------------------------+
		| Id   | The key ID/fingerprint of the newly generated key |
		+------+---------------------------------------------------+
		"""

		opts = {"type": type, "size": size}
		kwargs.setdefault("opts", {}).update(opts)
		args = (key_name,)

		return self._client.request('/key/gen', args, decoder='json', **kwargs)


	#TODO: Add `import(name, pam, password)`


	@base.returns_single_item
	def list(self, **kwargs):
		"""Returns a list of generated public keys that can be used with
		:meth:`~ipfshttpclient.Client.name.publish`.

		.. code-block:: python

			>>> client.key.list()
			{'Keys': [
				{'Name': 'self',
				 'Id': 'QmQf22bZar3WKmojipms22PkXH1MZGmvsqzQtuSvQE3uhm'},
				{'Name': 'example_key_name',
				 'Id': 'QmQLaT5ZrCfSkXTH6rUKtVidcxj8jrW3X2h75Lug1AV7g8'}
			]}

		Returns
		-------
			dict
		
		+------+--------------------------------------------------------+
		| Keys | List of dictionaries with Names and Ids of public keys |
		+------+--------------------------------------------------------+
		"""
		return self._client.request('/key/list', decoder='json', **kwargs)
	
	
	@base.returns_single_item
	def rename(self, key_name, new_key_name, **kwargs):
		"""Rename a keypair

		.. code-block:: python

			>>> client.key.rename("bla", "personal")
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
			dict
				Information about the key renameal
		"""
		args = (key_name, new_key_name)
		return self._client.request(
			'/key/rename', args, decoder='json', **kwargs
		)
	
	
	@base.returns_single_item
	def rm(self, key_name, *key_names, **kwargs):
		"""Remove a keypair

		.. code-block:: python

			>>> client.key.rm("bla")
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
			dict
		
		+------+--------------------------------------------------+
		| Keys | List of key names and IDs that have been removed |
		+------+--------------------------------------------------+
		"""
		args = (key_name,) + key_names
		return self._client.request('/key/rm', args, decoder='json', **kwargs)
