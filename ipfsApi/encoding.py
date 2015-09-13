from __future__ import absolute_import

import json

from .exceptions import EncodingException


class Encoding(object):

    def parse(self, string):
        raise NotImplemented

    def encode(self, obj):
        raise NotImplemented


class Json(Encoding):
    name = 'json'

    def __init__(self):
        self.encoder = json.JSONEncoder()
        self.decoder = json.JSONDecoder()

    def parse(self, raw):
        """
        Some responses from the IPFS api are a concatenated string of JSON
        objects, which crashes json.loads(), so we need to use this instead as
        a general approach.
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
    try:
        return __encodings[name.lower()]()
    except KeyError:
        try:
            msg = "Invalid encoding: '{}'".format(name)
        except:
            msg = "Invalid encoding"
        raise EncodingException(msg)
