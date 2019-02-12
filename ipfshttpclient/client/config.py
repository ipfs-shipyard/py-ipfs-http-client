# -*- coding: utf-8 -*-
from __future__ import absolute_import

from . import base


class Section(base.SectionBase):
	@base.returns_single_item
	def get(self, **kwargs):
		#TODO: Support the optional `key` parameter
		"""Returns the current used server configuration.

		.. warning::

			The configuration file contains private key data that must be
			handled with care.

		.. code-block:: python

			>>> config = client.config.get()
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
	
	
	@base.returns_single_item
	def replace(self, config, **kwargs):
		"""Replaces the existing config with a user-defined config.

		Make sure to back up the config file first if neccessary, as this
		operation can't be undone.
		"""
		return self._client.request('/config/replace', (config,), decoder='json', **kwargs)
	
	
	@base.returns_single_item
	def set(self, key, value=None, **kwargs):
		"""Add or replace a configuration value.

		.. code-block:: python

			>>> client.config("Addresses.Gateway")
			{'Key': 'Addresses.Gateway', 'Value': '/ip4/127.0.0.1/tcp/8080'}
			>>> client.config("Addresses.Gateway", "/ip4/127.0.0.1/tcp/8081")
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