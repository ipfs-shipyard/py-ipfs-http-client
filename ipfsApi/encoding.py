"""Defines encoding related classes.

.. note::

    The XML and ProtoBuf encoders are currently not functional.
"""

from __future__ import absolute_import

import json
import pickle

import six

from . import exceptions


class Encoding(object):
    """Abstract base for a data parser/encoder interface.
    """

    def parse(self, string):
        """Parses string into corresponding encoding.

        Raises
        ------
        ~ipfsApi.exceptions.DecodingError

        Parameters
        ----------
        string : bytes
            Data to be parsed
        """
        raise NotImplemented

    def encode(self, obj):
        """Serialize a raw object into corresponding encoding.

        Raises
        ------
        ~ipfsApi.exceptions.EncodingError

        Parameters
        ----------
        obj : object
            Object to be encoded
        """
        raise NotImplemented


class Json(Encoding):
    """JSON parser/encoder that handles concatenated JSON.
    """
    name = 'json'

    def parse(self, raw):
        """Returns a Python object decoded from JSON object(s) bytes.

        Raises
        ------
        ~ipfsApi.exceptions.DecodingError

        Parameters
        ----------
        raw : bytes
            Stringified JSON object

        Returns
        -------
            str | list | dict | int
        """
        json_string = raw.strip()
        decoder = json.JSONDecoder()
        results = []

        try:
            # Python 3 requires this to be a text string
            if isinstance(json_string, six.binary_type):
                json_string = json_string.decode("utf-8")

            # Some responses from the IPFS api are a concatenated string of
            # JSON objects, which crashes json.loads(), so we need to use this
            # instead as a general approach.
            obj, idx = decoder.raw_decode(json_string)
            results.append(obj)
            cur = idx
            while cur < len(json_string) - 1:
                if json_string[cur] == '\n':
                    cur += 1
                obj, idx = decoder.raw_decode(json_string[cur:])
                results.append(obj)
                cur += idx
        except (UnicodeDecodeError, ValueError) as error:
            raise exceptions.DecodingError('json', error)

        if len(results) == 1:
            return results[0]
        return results

    def encode(self, obj):
        """Returns ``obj`` serialized as JSON formatted bytes.

        Raises
        ------
        ~ipfsApi.exceptions.EncodingError

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
    """Python object parser/encoder using pickle.
    """
    name = 'pickle'

    def parse(self, raw):
        r"""Returns a Python object decoded from a pickle byte stream.

        .. code-block:: python

            >>> p = Pickle()
            >>> p.parse(b'(lp0\nI1\naI2\naI3\naI01\naF4.5\naNaF6000.0\na.')
            [1, 2, 3, True, 4.5, None, 6000.0]

        Raises
        ------
        ~ipfsApi.exceptions.DecodingError

        Parameters
        ----------
        raw : bytes
            Pickle data bytes

        Returns
        -------
            object
        """
        try:
            return pickle.loads(raw)
        except pickle.UnpicklingError as error:
            raise exceptions.DecodingError('pickle', error)

    def encode(self, obj):
        """Returns ``obj`` serialized as a pickle binary string.

        Raises
        ------
        ~ipfsApi.exceptions.EncodingError

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
    ~ipfsApi.exceptions.EncoderMissingError

    Parameters
    ----------
    name : str
        Encoding name. Supported options:

         * ``"json"``
         * ``"pickle"``
         * ``"protobuf"``
         * ``"xml"``
    """
    try:
        return __encodings[name.lower()]()
    except KeyError:
        raise exceptions.EncoderMissingError(name)
