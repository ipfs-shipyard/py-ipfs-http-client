"""Test the generic data encoding and decoding module."""
import json

import pytest

import ipfshttpclient.encoding
import ipfshttpclient.exceptions



@pytest.fixture
def json_encoder():
	return ipfshttpclient.encoding.Json()


def test_dummy_encoder():
	"""Tests if the dummy encoder does its trivial job"""
	dummy_encoder = ipfshttpclient.encoding.Dummy()
	
	for v in (b"123", b"4", b"ddjlflsdmlflsdfjlfjlfdsjldfs"):
		assert dummy_encoder.encode(v) == v
		
		assert list(dummy_encoder.parse_partial(v)) == [v]
	assert list(dummy_encoder.parse_finalize()) == []


def test_json_parse_partial(json_encoder):
	"""Tests if feeding parts of JSON strings in the right order to the JSON parser produces the right results."""
	data1 = {'key1': 'value1'}
	data2 = {'key2': 'value2'}
	
	# Try single fragmented data set
	data1_binary = json.dumps(data1).encode("utf-8")
	assert list(json_encoder.parse_partial(data1_binary[:8])) == []
	assert list(json_encoder.parse_partial(data1_binary[8:])) == [data1]
	assert list(json_encoder.parse_finalize()) == []
	
	# Try multiple data sets contained in whitespace
	data2_binary = json.dumps(data2).encode("utf-8")
	data2_final  = b"  " + data1_binary + b"  \r\n  " + data2_binary + b"  "
	assert list(json_encoder.parse_partial(data2_final)) == [data1, data2]
	assert list(json_encoder.parse_finalize()) == []
	
	# String containing broken UTF-8
	with pytest.raises(ipfshttpclient.exceptions.DecodingError):
		list(json_encoder.parse_partial(b'{"hello": "\xc3ber world!"}'))
	assert list(json_encoder.parse_finalize()) == []


def test_json_with_newlines(json_encoder):
	"""Tests if feeding partial JSON strings with line breaks behaves as expected."""
	data1 = '{"key1":\n"value1",\n'
	data2 = '"key2":\n\n\n"value2"\n}'
	
	data_expected = json.loads(data1 + data2)
	
	assert list(json_encoder.parse_partial(data1.encode("utf-8"))) == []
	assert list(json_encoder.parse_partial(data2.encode("utf-8"))) == [data_expected]
	assert list(json_encoder.parse_finalize()) == []


def test_json_parse_incomplete(json_encoder):
	"""Tests if feeding the JSON parse incomplete data correctly produces an error."""
	list(json_encoder.parse_partial(b'{"bla":'))
	with pytest.raises(ipfshttpclient.exceptions.DecodingError):
		json_encoder.parse_finalize()
	
	list(json_encoder.parse_partial(b'{"\xc3')) # Incomplete UTF-8 sequence
	with pytest.raises(ipfshttpclient.exceptions.DecodingError):
		json_encoder.parse_finalize()


def test_json_encode(json_encoder):
	"""Tests serialization of an object into a JSON formatted UTF-8 string."""
	data = {'key': 'value with Ünicøde characters ☺'}
	assert json_encoder.encode(data) == \
	       b'{"key":"value with \xc3\x9cnic\xc3\xb8de characters \xe2\x98\xba"}'

def test_json_encode_invalid_surrogate(json_encoder):
	"""Tests serialization of an object into a JSON formatted UTF-8 string."""
	data = {'key': 'value with Ünicøde characters and disallowed surrgate: \uDC00'}
	with pytest.raises(ipfshttpclient.exceptions.EncodingError):
		json_encoder.encode(data)

def test_json_encode_invalid_type(json_encoder):
	"""Tests serialization of an object into a JSON formatted UTF-8 string."""
	data = {'key': b'value that is not JSON encodable'}
	with pytest.raises(ipfshttpclient.exceptions.EncodingError):
		json_encoder.encode(data)


def test_get_encoder_by_name():
	"""Tests the process of obtaining an Encoder object given the named encoding."""
	encoder = ipfshttpclient.encoding.get_encoding('json')
	assert encoder.name == 'json'


def test_get_invalid_encoder():
	"""Tests the exception handling given an invalid named encoding."""
	with pytest.raises(ipfshttpclient.exceptions.EncoderMissingError):
		ipfshttpclient.encoding.get_encoding('fake')
