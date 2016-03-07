import unittest
import json
from httmock import urlmatch, HTTMock

import ipfsApi.encoding
import ipfsApi.exceptions


class TestEncoding(unittest.TestCase):
    def setUp(self):
        self.encoder = ipfsApi.encoding.Json()

    def test_json_parse(self):
        data = {'key': 'value'}
        raw = json.dumps(data)
        res = self.encoder.parse(raw)
        self.assertEqual(res['key'], 'value')

    def test_json_parse_chained(self):
        data1 = {'key1': 'value1'}
        data2 = {'key2': 'value2'}
        res = self.encoder.parse(
            json.dumps(data1) + json.dumps(data2))
        self.assertEqual(len(res), 2)
        self.assertEqual(res[0]['key1'], 'value1')
        self.assertEqual(res[1]['key2'], 'value2')

    def test_json_parse_chained_newlines(self):
        data1 = {'key1': 'value1'}
        data2 = {'key2': 'value2'}
        res = self.encoder.parse(
            json.dumps(data1) + '\n' + json.dumps(data2))
        self.assertEqual(len(res), 2)
        self.assertEqual(res[0]['key1'], 'value1')
        self.assertEqual(res[1]['key2'], 'value2')

    def test_json_encode(self):
        data = {'key': 'value'}
        self.assertEqual(
            self.encoder.encode(data),
            json.dumps(data))

    def test_get_encoder_by_name(self):
        encoder = ipfsApi.encoding.get_encoding('json')
        self.assertEqual(encoder.name, 'json')

    def test_get_invalid_encoder(self):
        self.assertRaises(ipfsApi.exceptions.EncodingException,
                          ipfsApi.encoding.get_encoding, 'fake')
