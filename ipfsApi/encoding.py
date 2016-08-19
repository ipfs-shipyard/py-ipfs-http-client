"""Defines encoding related classes.

.. note::

    The XML and ProtoBuf encoders are currently not functional.
"""

from __future__ import absolute_import

import json

from .exceptions import EncodingException


class Encoding(object):
    """Abstract base for a data parser/encoder interface.
    """

    def parse(self, string):
        """Parses string into corresponding encoding.

        Parameters
        ----------
        string : str
            String to be parsed
        """
        raise NotImplemented

    def encode(self, obj):
        """Serialize a raw object into corresponding encoding.

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

    def __init__(self):
        self.encoder = json.JSONEncoder()
        self.decoder = json.JSONDecoder()

    def parse(self, raw):
        """Returns a Python object decoded from JSON object(s) in raw.

        Some responses from the IPFS api are a concatenated string of JSON
        objects, which crashes json.loads(), so we need to use this instead as
        a general approach.

        Parameters
        ----------
        raw : str
            Stringified JSON object
        """
        json_string = raw.strip()
        results = []

        obj, idx = self.decoder.raw_decode(json_string)
        results.append(obj)
        cur = idx
        while cur < len(json_string) - 1:
            if json_string[cur] == '\n':
                cur += 1
            obj, idx = self.decoder.raw_decode(json_string[cur:])
            results.append(obj)
            cur += idx

        if len(results) == 1:
            return results[0]
        return results

    def encode(self, obj):
        """Returns obj serialized as JSON formatted string.

        Parameters
        ----------
        obj : str | list | dict | int | None
            JSON serializable Python object
        """
        return json.dumps(obj)


class Protobuf(Encoding):
    """Protobuf parser/encoder that handles protobuf."""
    name = 'protobuf'


class Xml(Encoding):
    """XML parser/encoder that handles XML."""
    name = 'xml'

# encodings supported by the IPFS api (default is JSON)
__encodings = {
    Json.name: Json,
    Protobuf.name: Protobuf,
    Xml.name: Xml
}


def get_encoding(name):
    """
    Returns an Encoder object for the named encoding

    Parameters
    ----------
    name : str
        Encoding name. Supported options:

         * ``"json"``
         * ``"protobuf"``
         * ``"xml"``
    """
    try:
        return __encodings[name.lower()]()
    except KeyError:
        try:
            msg = "Invalid encoding: '{}'".format(name)
        except:
            msg = "Invalid encoding"
        raise EncodingException(msg)
