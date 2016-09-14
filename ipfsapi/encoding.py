# -*- encoding: utf-8 -*-
"""Defines encoding related classes.

.. note::

    The XML and ProtoBuf encoders are currently not functional.
"""

from __future__ import absolute_import

import abc
import codecs
import io
import json
import pickle

import six

from . import exceptions


class Encoding(object):
    """Abstract base for a data parser/encoder interface.
    """
    __metaclass__ = abc.ABCMeta


    @abc.abstractmethod
    def parse_partial(self, raw):
        """Parses the given data and yields all complete data sets that can
        be built from this.

        Raises
        ------
        ~ipfsapi.exceptions.DecodingError

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
           ~ipfsapi.exceptions.DecodingError

        Returns
        -------
            generator
        """
        return ()


    def parse(self, raw):
        """Returns a Python object decoded from the bytes of this encoding.

        Raises
        ------
        ~ipfsapi.exceptions.DecodingError

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
        ~ipfsapi.exceptions.EncodingError

        Parameters
        ----------
        obj : object
            Object to be encoded
        """


class Dummy(Encoding):
    """Dummy parser/encoder that does nothing.
    """
    name = "none"

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
        self._buffer    = ""
        self._decoder1  = codecs.getincrementaldecoder('utf-8')()
        self._decoder2  = json.JSONDecoder()
        self._lasterror = None


    def parse_partial(self, data):
        """Incrementally decodes JSON data sets into Python objects.

        Raises
        ------
        ~ipfsapi.exceptions.DecodingError

        Returns
        -------
            generator
        """
        try:
            # Python 3 requires all JSON data to be a text string
            self._buffer += self._decoder1.decode(data, False)
        except UnicodeDecodeError as error:
            raise exceptions.DecodingError('json', error)

        # Process data buffer
        try:
            while True:
                # Make sure buffer does not start with whitespace
                #PERF: `.lstrip()` does not reallocate if the string does
                #      not actually start with whitespace.
                self._buffer = self._buffer.lstrip()

                # Try decoding the partial data buffer and return results
                # from this
                (obj, idx) = self._decoder2.raw_decode(self._buffer)

                # Decoding succeeded – yield result and shorten buffer
                yield obj
                self._buffer = self._buffer[idx:]
        except ValueError as error:
            # It is unfortunately not possible to reliably detect whether
            # parsing ended because of an error *within* the JSON string, or
            # an unexpected *end* of the JSON string.
            # We therefor have to assume that any error that occurs here
            # *might* be related to the JSON parser hitting EOF and therefor
            # have to postpone error reporting until `parse_finalize` is
            # called.
            self._lasterror = error

    def parse_finalize(self):
        """Raises errors for incomplete buffered data that could not be parsed
        because the end of the input data has been reached.

        Raises
        ------
        ~ipfsapi.exceptions.DecodingError

        Returns
        -------
            tuple : Always empty
        """
        try:
            try:
                # Raise exception for remaining bytes in bytes decoder
                self._decoder1.decode(b'', True)
            except UnicodeDecodeError as error:
                raise exceptions.DecodingError('json', error)

            # Late raise errors that looked like they could have been fixed if the
            # caller had provided more data
            if self._buffer:
                raise exceptions.DecodingError('json', self._lasterror)
        finally:
            # Reset state
            self._buffer    = ""
            self._lasterror = None
            self._decoder1.reset()

        return ()


    def encode(self, obj):
        """Returns ``obj`` serialized as JSON formatted bytes.

        Raises
        ------
        ~ipfsapi.exceptions.EncodingError

        Parameters
        ----------
        obj : str | list | dict | int
            JSON serializable Python object

        Returns
        -------
            bytes
        """
        try:
            result = json.dumps(obj)
            if isinstance(result, six.text_type):
                return result.encode("utf-8")
            else:
                return result
        except (UnicodeEncodeError, TypeError) as error:
            raise exceptions.EncodingError('json', error)


class Pickle(Encoding):
    """Python object parser/encoder using `pickle`.
    """
    name = 'pickle'

    def __init__(self):
        self._buffer = io.BytesIO()

    def parse_partial(self, raw):
        """Buffers the given data so that the it can be passed to `pickle` in
        one go.
        
        This does not actually process the data in smaller chunks, but merely
        buffers it until `parse_finalize` is called! This is mostly because
        the standard-library module expects the entire data to be available up
        front, which is currently always the case for our code anyways.

        Parameters
        ----------
        raw : bytes
            Data to be buffered

        Returns
        -------
            tuple : An empty tuple
        """
        self._buffer.write(raw)
        return ()

    def parse_finalize(self):
        """Parses the buffered data and yields the result.

        Raises
        ------
           ~ipfsapi.exceptions.DecodingError

        Returns
        -------
            generator
        """
        try:
            self._buffer.seek(0, 0)
            yield pickle.load(self._buffer)
        except pickle.UnpicklingError as error:
            raise exceptions.DecodingError('pickle', error)

    def parse(self, raw):
        r"""Returns a Python object decoded from a pickle byte stream.

        .. code-block:: python

            >>> p = Pickle()
            >>> p.parse(b'(lp0\nI1\naI2\naI3\naI01\naF4.5\naNaF6000.0\na.')
            [1, 2, 3, True, 4.5, None, 6000.0]

        Raises
        ------
        ~ipfsapi.exceptions.DecodingError

        Parameters
        ----------
        raw : bytes
            Pickle data bytes

        Returns
        -------
            object
        """
        return Encoding.parse(self, raw)

    def encode(self, obj):
        """Returns ``obj`` serialized as a pickle binary string.

        Raises
        ------
        ~ipfsapi.exceptions.EncodingError

        Parameters
        ----------
        obj : object
            Serializable Python object

        Returns
        -------
            bytes
        """
        try:
            return pickle.dumps(obj)
        except pickle.PicklingError as error:
            raise exceptions.EncodingError('pickle', error)


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
    Pickle.name: Pickle,
    Protobuf.name: Protobuf,
    Xml.name: Xml
}


def get_encoding(name):
    """
    Returns an Encoder object for the named encoding

    Raises
    ------
    ~ipfsapi.exceptions.EncoderMissingError

    Parameters
    ----------
    name : str
        Encoding name. Supported options:

         * ``"none"``
         * ``"json"``
         * ``"pickle"``
         * ``"protobuf"``
         * ``"xml"``
    """
    try:
        return __encodings[name.lower()]()
    except KeyError:
        raise exceptions.EncoderMissingError(name)
