"""Defines encoding related classes.

Classes:
Encoding - An abstract based for a data parser/encoder interface.
Json - A subclass of Encoding that handles JSON parsing and encoding.
Protobuf - A subclass of Encoding to handle Protobuf parsing/encoding. TO DO
Xml - A subclass of Encoding to handle Xml parsing and encoding. TO DO

Functions:
get_encoding(name) - Retrieves the Encoder object for the named encoding.
"""

from __future__ import absolute_import

import json

from .exceptions import EncodingException


class Encoding(object):
    """Abstract base for a data parser/encoder interface.

    Public methods:
    parse -- parses string into corresponding encoding
    encode - serialize a raw object into corresponding encoding
    """

    def parse(self, string):
        """Parses string into corresponding encoding.

        Keyword arguments:
            string - string to be parsed
        """
        raise NotImplemented

    def encode(self, obj):
        """Serialize a raw object into corresponding encoding.

        Keyword arguments:
            obj - object to be encoded.
        """
        raise NotImplemented


class Json(Encoding):
    """JSON parser/encoder that handles concatenated JSON.

    Public methods:
    __init__ -- creates a Json encoder/decoder
    parse --  returns a Python object decoded from JSON object(s) in raw
    encode -- returns obj serialized as JSON formatted string
    """
    name = 'json'

    def __init__(self):
        """Creates a JSON encoder/decoder"""
        self.encoder = json.JSONEncoder()
        self.decoder = json.JSONDecoder()

    def parse(self, raw):
        """Returns a Python object decoded from JSON object(s) in raw

        Some responses from the IPFS api are a concatenated string of JSON
        objects, which crashes json.loads(), so we need to use this instead as
        a general approach.

        Keyword arguments:
        raw -- raw JSON object
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
        """
        Returns obj serialized as JSON formatted string

        Keyword arguments:
        obj -- generic Python object
        """
        return json.dumps(obj)


class Protobuf(Encoding):
    """Protobuf parser/encoder that handles protobuf."""
    name = 'protobuf'


class Xml(Encoding):
    """XML parser/encoder that handles XML."""
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

    Keyword arguments:
    name - named encoding. Supported options: Json, Protobuf, Xml
    """
    try:
        return __encodings[name.lower()]()
    except KeyError:
        try:
            msg = "Invalid encoding: '{}'".format(name)
        except:
            msg = "Invalid encoding"
        raise EncodingException(msg)
