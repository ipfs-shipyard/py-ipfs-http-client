# -*- encoding: utf-8 -*-
"""Defines encoding related classes.

.. note::

	The XML and ProtoBuf encoders are currently not functional.
"""

from __future__ import absolute_import

import abc
import codecs
import json

import six

from . import exceptions


class Encoding(object):
	"""Abstract base for a data parser/encoder interface.
	"""
	__metaclass__ = abc.ABCMeta

	is_stream = False

	@abc.abstractmethod
	def parse_partial(self, raw):
		"""Parses the given data and yields all complete data sets that can
		be built from this.

		Raises
		------
		~ipfshttpclient.exceptions.DecodingError

		Parameters
		----------
		raw : bytes
			Data to be parsed

		Returns
		-------
			generator
		"""

	def parse_finalize(self):
		"""Finalizes parsing based on remaining buffered data and yields the
		remaining data sets.

		Raises
		------
		   ~ipfshttpclient.exceptions.DecodingError

		Returns
		-------
			generator
		"""
		return ()

	def parse(self, raw):
		"""Returns a Python object decoded from the bytes of this encoding.

		Raises
		------
		~ipfshttpclient.exceptions.DecodingError

		Parameters
		----------
		raw : bytes
			Data to be parsed

		Returns
		-------
			object
		"""
		results = list(self.parse_partial(raw))
		results.extend(self.parse_finalize())
		return results[0] if len(results) == 1 else results

	@abc.abstractmethod
	def encode(self, obj):
		"""Serialize a raw object into corresponding encoding.

		Raises
		------
		~ipfshttpclient.exceptions.EncodingError

		Parameters
		----------
		obj : object
			Object to be encoded
		"""


class Dummy(Encoding):
	"""Dummy parser/encoder that does nothing.
	"""
	name = "none"
	is_stream = True

	def parse_partial(self, raw):
		"""Yields the data passed into this method.

		Parameters
		----------
		raw : bytes
			Any kind of data

		Returns
		-------
			generator
		"""
		yield raw

	def encode(self, obj):
		"""Returns the bytes representation of the data passed into this
		function.

		Parameters
		----------
		obj : object
			Any Python object

		Returns
		-------
			bytes
		"""
		return six.b(str(obj))


class Json(Encoding):
	"""JSON parser/encoder that handles concatenated JSON.
	"""
	name = 'json'

	def __init__(self):
		self._buffer    = []
		self._decoder1  = codecs.getincrementaldecoder('utf-8')()
		self._decoder2  = json.JSONDecoder()
		self._lasterror = None

	def parse_partial(self, data):
		"""Incrementally decodes JSON data sets into Python objects.

		Raises
		------
		~ipfshttpclient.exceptions.DecodingError

		Returns
		-------
			generator
		"""
		try:
			# Python 3 requires all JSON data to be a text string
			lines = self._decoder1.decode(data, False).split("\n")

			# Add first input line to last buffer line, if applicable, to
			# handle cases where the JSON string has been chopped in half
			# at the network level due to streaming
			if len(self._buffer) > 0 and self._buffer[-1] is not None:
				self._buffer[-1] += lines[0]
				self._buffer.extend(lines[1:])
			else:
				self._buffer.extend(lines)
		except UnicodeDecodeError as error:
			six.raise_from(exceptions.DecodingError('json', error), error)

		# Process data buffer
		index = 0
		try:
			# Process each line as separate buffer
			#PERF: This way the `.lstrip()` call becomes almost always a NOP
			#      even if it does return a different string it will only
			#      have to allocate a new buffer for the currently processed
			#      line.
			while index < len(self._buffer):
				while self._buffer[index]:
					# Make sure buffer does not start with whitespace
					#PERF: `.lstrip()` does not reallocate if the string does
					#      not actually start with whitespace.
					self._buffer[index] = self._buffer[index].lstrip()

					# Handle case where the remainder of the line contained
					# only whitespace
					if not self._buffer[index]:
						self._buffer[index] = None
						continue

					# Try decoding the partial data buffer and return results
					# from this
					data = self._buffer[index]
					for index2 in range(index, len(self._buffer)):
						# If decoding doesn't succeed with the currently
						# selected buffer (very unlikely with our current
						# class of input data) then retry with appending
						# any other pending pieces of input data
						# This will happen with JSON data that contains
						# arbitrary new-lines: "{1:\n2,\n3:4}"
						if index2 > index:
							data += "\n" + self._buffer[index2]

						try:
							(obj, offset) = self._decoder2.raw_decode(data)
						except ValueError:
							# Treat error as fatal if we have already added
							# the final buffer to the input
							if (index2 + 1) == len(self._buffer):
								raise
						else:
							index = index2
							break

					# Decoding succeeded – yield result and shorten buffer
					yield obj
					if offset < len(self._buffer[index]):
						self._buffer[index] = self._buffer[index][offset:]
					else:
						self._buffer[index] = None
				index += 1
		except ValueError as error:
			# It is unfortunately not possible to reliably detect whether
			# parsing ended because of an error *within* the JSON string, or
			# an unexpected *end* of the JSON string.
			# We therefor have to assume that any error that occurs here
			# *might* be related to the JSON parser hitting EOF and therefor
			# have to postpone error reporting until `parse_finalize` is
			# called.
			self._lasterror = error
		finally:
			# Remove all processed buffers
			del self._buffer[0:index]

	def parse_finalize(self):
		"""Raises errors for incomplete buffered data that could not be parsed
		because the end of the input data has been reached.

		Raises
		------
		~ipfshttpclient.exceptions.DecodingError

		Returns
		-------
			tuple : Always empty
		"""
		try:
			try:
				# Raise exception for remaining bytes in bytes decoder
				self._decoder1.decode(b'', True)
			except UnicodeDecodeError as error:
				six.raise_from(exceptions.DecodingError('json', error), error)

			# Late raise errors that looked like they could have been fixed if
			# the caller had provided more data
			if self._buffer:
				six.raise_from(exceptions.DecodingError('json', self._lasterror), self._lasterror)
		finally:
			# Reset state
			self._buffer    = []
			self._lasterror = None
			self._decoder1.reset()

		return ()

	def encode(self, obj):
		"""Returns ``obj`` serialized as JSON formatted bytes.

		Raises
		------
		~ipfshttpclient.exceptions.EncodingError

		Parameters
		----------
		obj : Union[str, list, dict, int]
			JSON serializable Python object

		Returns
		-------
			bytes
		"""
		try:
			result = json.dumps(obj, sort_keys=True, indent=None,
			                    separators=(',', ':'), ensure_ascii=False)
			if isinstance(result, six.text_type):  #PY3
				return result.encode("utf-8")
			else:  #PY2
				return result
		except (UnicodeEncodeError, TypeError) as error:
			six.raise_from(exceptions.EncodingError('json', error), error)


class Protobuf(Encoding):
	"""Protobuf parser/encoder that handles protobuf."""
	name = 'protobuf'


class Xml(Encoding):
	"""XML parser/encoder that handles XML."""
	name = 'xml'


# encodings supported by the IPFS api (default is JSON)
__encodings = {
	Dummy.name: Dummy,
	Json.name: Json,
	Protobuf.name: Protobuf,
	Xml.name: Xml
}


def get_encoding(name):
	"""
	Returns an Encoder object for the named encoding

	Raises
	------
	~ipfshttpclient.exceptions.EncoderMissingError

	Parameters
	----------
	name : str
		Encoding name. Supported options:

		 * ``"none"``
		 * ``"json"``
		 * ``"protobuf"``
		 * ``"xml"``
	"""
	try:
		return __encodings[name.lower()]()
	except KeyError:
		six.raise_from(exceptions.EncoderMissingError(name), None)
