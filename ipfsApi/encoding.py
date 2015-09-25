from __future__ import absolute_import

import json

from .exceptions import EncodingException


class Encoding(object):
    """
    Abstract base for a data parser/encoder interface interface
    """

    def parse(self, string):
        raise NotImplemented

    def encode(self, obj):
        raise NotImplemented


class Json(Encoding):
    """
    JSON parser/encoder that handles concatenated JSON
    """
    name = 'json'

    def __init__(self):
        self.encoder = json.JSONEncoder()
        self.decoder = json.JSONDecoder()

    def parse(self, raw):
        """
        Returns a Python object decoded from JSON object(s) in raw

        Some responses from the IPFS api are a concatenated string of JSON
        objects, which crashes json.loads(), so we need to use this instead as
        a general approach.

        >>> coder = Json()
        >>> coder.parse("[0, 1, 2, 3][4, 5, 6, 7]")
        [[0, 1, 2, 3], [4, 5, 6, 7]]
        """
        json_string = raw.strip()
        results = []

        obj, idx = self.decoder.raw_decode(json_string)
        results.append(obj)
        cur = idx
        while cur < len(json_string) - 1:
            obj, idx = self.decoder.raw_decode(json_string[cur:])
            results.append(obj)
            cur += idx

        if len(results) == 1:
            return results[0]
        return results

    def encode(self, obj):
        """
        Returns obj encoded as JSON in a binary string

        >>> coder = Json()
        >>> coder.encode([0, 1, 2, 3])
        "[0, 1, 2, 3]"
        """
        return json.dumps(obj)


class Protobuf(Encoding):
    name = 'protobuf'


class Xml(Encoding):
    name = 'xml'

# encodings supported by the IPFS api (default is json)
__encodings = {
    Json.name: Json,
    Protobuf.name: Protobuf,
    Xml.name: Xml
}


def get_encoding(name):
    """
    Returns an Encoder object for the named encoding

    >>> get_encoding('json') # doctest: +ELLIPSIS
    <ipfsApi.encoding.Json object at 0x...>
    >>> get_encoding('JSON').encode([0, 1, 2, 3])
    "[0, 1, 2, 3]"

    >>> encoding.get_encoding('foo')
    Traceback (most recent call last):
      ...
    ipfsApi.exceptions.EncodingException: Invalid encoding: 'foo'
    """
    try:
        return __encodings[name.lower()]()
    except KeyError:
        try:
            msg = "Invalid encoding: '{}'".format(name)
        except:
            msg = "Invalid encoding"
        raise EncodingException(msg)
