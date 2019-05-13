# -*- coding: utf-8 -*-
from __future__ import absolute_import

import warnings

from . import DEFAULT_HOST, DEFAULT_PORT, DEFAULT_BASE


class DeprecatedMethodProperty(object):
	def __init__(self, *path, **kwargs):
		#PY2: No support for kw-only parameters after glob parameters
		prefix = kwargs.pop("prefix", [])
		strip  = kwargs.pop("strip", 0)
		assert not kwargs

		self.props  = path
		self.path   = tuple(prefix) + (path[:-strip] if strip > 0 else tuple(path))
		self.warned = False

		self.__help__ = "Deprecated method: Please use “client.{0}” instead".format(
			".".join(self.path)
		)

	def __get__(self, obj, type=None):
		if not self.warned:
			message = "IPFS API function “{0}” has been renamed to “{1}”".format(
				"_".join(self.path), ".".join(self.path)
			)
			warnings.warn(message, FutureWarning)
			self.warned = True
		
		for name in self.props:
			print(name, obj)
			obj = getattr(obj, name)
		return obj
