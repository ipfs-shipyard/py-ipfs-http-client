"""Defines encoding related classes.

Classes:
TestEncoding - A class that tests constructs located in the encoding.py module.
"""

import unittest
import json
import pickle

from httmock import urlmatch, HTTMock

import ipfsApi.encoding
import ipfsApi.exceptions


class TestEncoding(unittest.TestCase):
    """Unit tests the Encoding class

    Public methods:
    setUp - create a Json encoder 
    test_json_parse - Asserts parsed key/value json matches expected output
    test_json_parse_chained - Tests if concatenated string of JSON object is being parsed correctly
    test_json_parse_chained_newlines - Tests parsing of concatenated string of JSON object containing a new line
    test_json_encode - Tests serilization of json formatted string to an object
    test_get_encoder_by_name - Tests the process of obtaining an Encoder object given the named encoding
    test_get_invalid_encoder - Tests the exception handling given an invalid named encoding

    """
    def setUp(self):
        """create a Json encoder"""
        self.encoder_json = ipfsApi.encoding.Json()
        self.encoder_pickle = ipfsApi.encoding.Pickle()

    def test_json_parse(self):
        """Asserts parsed key/value json matches expected output."""
        data = {'key': 'value'}
        raw = json.dumps(data)
        res = self.encoder_json.parse(raw)
        self.assertEqual(res['key'], 'value')

    def test_json_parse_chained(self):
        """Tests if concatenated string of JSON object is being parsed correctly."""
        data1 = {'key1': 'value1'}
        data2 = {'key2': 'value2'}
        res = self.encoder_json.parse(
            json.dumps(data1) + json.dumps(data2))
        self.assertEqual(len(res), 2)
        self.assertEqual(res[0]['key1'], 'value1')
        self.assertEqual(res[1]['key2'], 'value2')

    def test_json_parse_chained_newlines(self):
        """Tests parsing of concatenated string of JSON object containing a new line."""
        data1 = {'key1': 'value1'}
        data2 = {'key2': 'value2'}
        res = self.encoder_json.parse(
            json.dumps(data1) + '\n' + json.dumps(data2))
        self.assertEqual(len(res), 2)
        self.assertEqual(res[0]['key1'], 'value1')
        self.assertEqual(res[1]['key2'], 'value2')

    def test_json_encode(self):
        """Tests serilization of json formatted string into an object."""
        data = {'key': 'value'}
        self.assertEqual(
            self.encoder_json.encode(data),
            json.dumps(data))

    def test_encode_pickle(self):
        """Tests serilization of pickle formatted string into an object."""
        # In Python 2, data appears to be encoded differently based on the
        # context from which pickle.dumps() is called. For this reason we are
        # encoding and then decoding data to ensure that the decoded values are
        # equivalent after the original data has been serialized.
        data = {'key': 'value'}
        encoder_res = pickle.loads(self.encoder_pickle.encode(data))
        pickle_res = pickle.loads(pickle.dumps(data))
        self.assertEqual(encoder_res, pickle_res)

    def test_parse_pickle(self):
        """Tests if pickled Python object matches expected output."""
        data = {'key': 'value'}
        raw = pickle.dumps(data)
        res = self.encoder_pickle.parse(raw)
        self.assertEqual(res['key'], 'value')

    def test_get_encoder_by_name(self):
        """Tests the process of obtaining an Encoder object given the named encoding."""
        encoder = ipfsApi.encoding.get_encoding('json')
        self.assertEqual(encoder.name, 'json')

    def test_get_invalid_encoder(self):
        """Tests the exception handling given an invalid named encoding."""
        self.assertRaises(ipfsApi.exceptions.EncoderMissingError,
                          ipfsApi.encoding.get_encoding, 'fake')
