"""Defines encoding related classes.

Classes:
TestEncoding - A class that tests constructs located in the encoding.py module.
"""

import unittest
import json
import pickle

import six
from httmock import urlmatch, HTTMock

import ipfsapi.encoding
import ipfsapi.exceptions


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
        self.encoder_json = ipfsapi.encoding.Json()
        self.encoder_pickle = ipfsapi.encoding.Pickle()

    def test_json_parse(self):
        """Asserts parsed key/value json matches expected output."""
        data = {'key': 'value'}
        raw = six.b(json.dumps(data))
        res = self.encoder_json.parse(raw)
        self.assertEqual(res['key'], 'value')

    def test_json_parse_partial(self):
        """Tests if feeding parts of JSON strings in the right order to the JSON parser produces the right results."""
        data1 = {'key1': 'value1'}
        data2 = {'key2': 'value2'}
        
        assertPartialEqual  = lambda d, r: self.assertEqual(list(self.encoder_json.parse_partial(d)), r)
        assertFinalizeEmpty = lambda:      self.assertEqual(list(self.encoder_json.parse_finalize()), [])
        
        # Try single fragmented data set
        data1_binary = six.b(json.dumps(data1))
        assertPartialEqual(data1_binary[:8], [])
        assertPartialEqual(data1_binary[8:], [data1])
        assertFinalizeEmpty()
        
        # Try multiple data sets contained in whitespace
        data2_binary = six.b(json.dumps(data2))
        assertPartialEqual(b"  " + data1_binary + b"  \r\n  " + data2_binary + b"  ", [data1, data2])
        assertFinalizeEmpty()
        
        # String containing broken UTF-8
        self.assertRaises(ipfsapi.exceptions.DecodingError,
                          lambda: list(self.encoder_json.parse_partial(b'{"hello": "\xc3ber world!"}')))
        assertFinalizeEmpty()
    
    def test_json_with_newlines(self):
        """Tests if feeding partial JSON strings with line breaks behaves as expected."""
        data1 = '{"key1":\n"value1",\n'
        data2 = '"key2":\n\n\n"value2"\n}'
        
        data_expected = json.loads(data1 + data2)
        
        assert list(self.encoder_json.parse_partial(six.b(data1))) == []
        assert list(self.encoder_json.parse_partial(six.b(data2))) == [data_expected]
        assert list(self.encoder_json.parse_finalize()) == []
    
    def test_json_parse_incomplete(self):
        """Tests if feeding the JSON parse incomplete data correctly produces an error."""
        list(self.encoder_json.parse_partial(b'{"bla":'))
        self.assertRaises(ipfsapi.exceptions.DecodingError,
                          self.encoder_json.parse_finalize)

        list(self.encoder_json.parse_partial(b'{"\xc3')) # Incomplete UTF-8 sequence
        self.assertRaises(ipfsapi.exceptions.DecodingError,
                          self.encoder_json.parse_finalize)

    def test_json_parse_chained(self):
        """Tests if concatenated string of JSON object is being parsed correctly."""
        data1 = {'key1': 'value1'}
        data2 = {'key2': 'value2'}
        res = self.encoder_json.parse(
            six.b(json.dumps(data1)) + six.b(json.dumps(data2)))
        self.assertEqual(len(res), 2)
        self.assertEqual(res[0]['key1'], 'value1')
        self.assertEqual(res[1]['key2'], 'value2')

    def test_json_parse_chained_newlines(self):
        """Tests parsing of concatenated string of JSON object containing a new line."""
        data1 = {'key1': 'value1'}
        data2 = {'key2': 'value2'}
        res = self.encoder_json.parse(
            six.b(json.dumps(data1)) + b'\n' + six.b(json.dumps(data2)))
        self.assertEqual(len(res), 2)
        self.assertEqual(res[0]['key1'], 'value1')
        self.assertEqual(res[1]['key2'], 'value2')

    def test_json_encode(self):
        """Tests serilization of json formatted string into an object."""
        data = {'key': 'value'}
        self.assertEqual(
            self.encoder_json.encode(data),
            b'{"key": "value"}')

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
        encoder = ipfsapi.encoding.get_encoding('json')
        self.assertEqual(encoder.name, 'json')

    def test_get_invalid_encoder(self):
        """Tests the exception handling given an invalid named encoding."""
        self.assertRaises(ipfsapi.exceptions.EncoderMissingError,
                          ipfsapi.encoding.get_encoding, 'fake')
