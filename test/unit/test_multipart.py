"""Test the file multipart.py

Classes:
TestContentHelpers -- test the three content-header helper functions
TestBodyGenerator -- test the BodyGenerator helper class
TestStreamBase -- test the StreamBase helper class
TestFileStream -- test the FileStream generator class
TestDirectoryStream -- test the DirectoryStream generator class
TestTextStream -- test the TextStream generator class
TestStreamHelpers -- unimplemented
"""

import io
import os
import re
import unittest
import urllib

import pytest
import six

from six.moves import urllib_parse

import ipfshttpclient.multipart

ENC = "UTF-8"

class TestContentHelpers(unittest.TestCase):
	"""Tests the functionality of the three content-oriented helper functions.

	Public methods:
	test_content_disposition_headers -- check the content_disposition defaults
	test_content_disposition_headers_with_type -- check that content_disposition
												  handles given disposition type
	test_content_headers_type -- check the content_type guessing functionality
	test_multipart_content_type_headers -- check multipart_content_type_headers functionality
	"""

	def test_content_disposition_headers(self):
		"""Check that content_disposition defaults properly"""
		expected = {'Content-Disposition': 'form-data; filename="example.txt"'}
		actual = ipfshttpclient.multipart.content_disposition_headers('example.txt')
		assert expected == actual

	def test_content_disposition_headers_with_type(self):
		"""Check that content_disposition handles given disposition type"""
		expected = {'Content-Disposition': 'attachment; filename="example.txt"'}
		actual = ipfshttpclient.multipart.content_disposition_headers('example.txt', 'attachment')
		assert expected == actual

	def test_content_type_headers(self):
		"""Check the content_type guessing functionality."""
		actual = ipfshttpclient.multipart.content_type_headers('example.txt')
		expected = {'Content-Type': 'text/plain'}
		assert expected == actual

		actual = ipfshttpclient.multipart.content_type_headers('example.jpeg')
		expected = {'Content-Type': 'image/jpeg'}
		assert expected == actual

		actual = ipfshttpclient.multipart.content_type_headers('example')
		expected = {'Content-Type': 'application/octet-stream'}
		assert expected == actual

	def test_multipart_content_type_headers(self):
		"""Check test_multipart_content_type_headers functionality."""
		actual = ipfshttpclient.multipart.multipart_content_type_headers('8K5rNKlLQVyreRNncxOTeg')
		expected = {'Content-Type': 'multipart/mixed; boundary="8K5rNKlLQVyreRNncxOTeg"'}
		assert expected == actual

		actual = ipfshttpclient.multipart.multipart_content_type_headers('8K5rNKlLQVyreRNncxOTeg', 'alt')
		expected = {'Content-Type': 'multipart/alt; boundary="8K5rNKlLQVyreRNncxOTeg"'}
		assert expected == actual


class TestBodyGenerator(unittest.TestCase):
	"""Tests the functionality of the BodyGenerator class.

	Public methods:
	"""




def _generate_test_chunks(chunk_size, interations):
	"""Generates strings of chunk_size length until out of iterations."""
	for i in range(interations):
		output = b""
		for j in range(chunk_size):
			output += b"z"
		yield output


class StreamBaseSub(ipfshttpclient.multipart.StreamBase):
	def _body(self):
		raise NotImplementedError()

class StreamFileMixinSub(ipfshttpclient.multipart.StreamBase, ipfshttpclient.multipart.StreamFileMixin):
	def _body(self):
		raise NotImplementedError()


class TestStreamBase(unittest.TestCase):
	"""Test the StreamBase class.

	Public methods:
	test_init -- test the default arguments of the constructor
	test_init_defaults -- tests the constructor and its behavior with only the required argument
	test_body -- verify that body is unimplemented
	test__gen_headers -- tests _gen_headers function against example output
	test__gen_item_start -- tests _gen_item_start function against example output
	test__gen_chunks -- test the _gen_chunks function against example output
	test__gen_end -- test the _gen_end function against example output
	"""

	def test_init(self):
		"""Test the __init__ function for default parameter values."""
		name = "test_name"
		instance = StreamBaseSub(name)
		assert instance.name == name

	def test_init_defaults(self):
		"""Test the __init__ function for default parameter values."""
		name = "test_name"
		expected_disposition = 'form-data; filename="test_name"'
		expected_type = r'multipart/form-data; boundary="\S*"'
		expected_boundary_pattern = r'\S*'
		generator = StreamBaseSub(name)
		assert generator._headers['Content-Disposition'] == expected_disposition
		assert re.search(expected_type,             generator.headers()['Content-Type'])
		assert re.search(expected_boundary_pattern, generator._boundary)

	def test_body(self):
		"""Ensure that body throws a NotImplemented exception."""
		instance = StreamBaseSub("name")
		with pytest.raises(NotImplementedError):
			instance._body()
			instance.body()

	def test__gen_headers(self):
		"""Test the _gen_headers function against sample output."""
		name = "test_name"
		generator = StreamBaseSub(name)

		expected = b'Connection: close\r\n' \
		         + b'Content-Disposition: form-data; filename="test_name"\r\n' \
		         + b'Content-Type: multipart/form-data; ' \
		         + b'boundary="' + generator._boundary.encode() + b'"\r\n\r\n'

		headers = b"".join(generator._gen_headers(generator._headers))
		assert headers == expected

	def test__gen_item_start(self):
		"""Test the _gen_item_start function against sample output."""
		expected = b'--test_boundary\r\n'
		name = "test_name"
		generator = StreamBaseSub(name)
		generator._boundary = "test_boundary"
		headers = b"".join(generator._gen_item_start())
		assert headers == expected

	def test__gen_item_end(self):
		"""Test the _gen_item_end function against sample output."""
		expected = b"\r\n"
		generator = StreamBaseSub("test")
		headers = b"".join(generator._gen_item_end())
		assert headers == expected

	def test__gen_chunks(self):
		"""Test the gen_chunks function against example output."""
		name = "fsdfgh"
		chunk_size = 2
		instance = StreamBaseSub(name, chunk_size)
		for i in instance._gen_chunks(_generate_test_chunks(5, 5)):
			assert len(i) <= chunk_size

	def test__gen_end(self):
		"""Test the close function against example output."""
		name = "fsdfgh"
		instance = StreamBaseSub(name)
		expected = b'--\\S+--\r\n'
		actual = b''
		for i in instance._gen_end():
			actual += i

		assert re.search(expected, actual)


class TestStreamFileMixin(unittest.TestCase):
	"""Test the StreamFileMixin class.

	Public methods:
	test__gen_file -- test the _gen_file function against example output
	test__gen_file_start -- test the _gen_file_start function against example output
	test__gen_file_chunks -- test the _gen_file_chunks function against example output
	test__gen_file_end -- test the _gen_file_end function against example output
	"""

	def do_test__gen_file(self, name, file_location, abspath):
		"""Test the _gen_file function against sample output."""
		generator = StreamFileMixinSub(name)
		file = io.BytesIO()
		file.write(b"!234")
		file.seek(0)

		expected = b'--' + generator._boundary.encode() + b'\r\n'
		expected += b'Abspath: ' + name.encode(ENC) + b'\r\n' if abspath else b''
		expected += b'Content-Disposition: file; '\
		         + b'filename="' + urllib_parse.quote_plus(name).encode(ENC) + b'"\r\n'\
			 + b'Content-Type: text/plain\r\n'\
			 + b'\r\n' \
		         + b'!234\r\n'

		headers = b"".join(generator._gen_file(name, file_location, file,
						       content_type="text/plain"))
		assert headers == expected

	def test__gen_file(self):
		self.do_test__gen_file("functional/fake_dir/fsdfgh",
					file_location=None, abspath=False)
	def test__gen_file_relative(self):
		filepath = "functional/fake_dir/fsdfgh"
		self.do_test__gen_file(filepath, filepath, abspath=False)
	def test__gen_file_absolute(self):
		filepath = "/functional/fake_dir/fsdfgh"
		self.do_test__gen_file(filepath, filepath, abspath=True)

	def do_test__gen_file_start(self, name, file_location, abspath):
		"""Test the _gen_file_start function against sample output."""
		generator = StreamFileMixinSub(name)

		expected = b'--' + generator._boundary.encode() + b'\r\n'
		expected += b'Abspath: ' + file_location.encode(ENC) + b'\r\n' if abspath else b''
		expected += b'Content-Disposition: file; filename="' + name.encode(ENC) + b'"\r\n'\
			  + b'Content-Type: application/octet-stream\r\n'\
			  + b'\r\n'

		headers = b"".join(generator._gen_file_start(name, file_location))
		assert headers == expected

	def test__gen_file_start(self):
		self.do_test__gen_file_start("test_name", file_location=None, abspath=False)
	def test__gen_file_start_with_filepath(self):
		name = "test_name"
		self.do_test__gen_file_start(name, os.path.join(os.path.sep, name), abspath=True)

	def test__gen_file_chunks(self):
		"""Test the _gen_file_chunks function against example output.

		Warning: This test depends on the contents of
		test/functional/fake_dir/fsdfgh
		Changing that file could break the test.
		"""
		name = "fsdfgh"
		chunk_size = 2
		path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
		                    "functional", "fake_dir", "fsdfgh")
		instance = StreamFileMixinSub(name, chunk_size)
		expected = 'dsadsad\n'
		output = ""
		open_file = open(path)
		for emitted in instance._gen_file_chunks(open_file):
			if type(emitted) is not str:
				emitted = emitted.decode()
			assert len(emitted) <= chunk_size
			output += emitted
		open_file.close()
		assert output == expected

	def test__gen_file_end(self):
		"""Test the _gen_file_end function against sample output."""
		expected = b"\r\n"
		generator = StreamFileMixinSub("test")
		headers = b"".join(generator._gen_file_end())
		assert headers == expected


class TestFilesStream(unittest.TestCase):
	"""Test the FileStream class

	Public methods:
	test_body -- check file stream body for proper structure
	"""

	def prep_test_body(self):
		"""Test the body function against expected output.

		Warning: This test depends on the contents of
		test/functional/fake_dir
		Changing that directory or its contents could break the test.
		"""
		# Get OS-agnostic path to test files
		path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
		                    "functional", "fake_dir")
		# Collect absolute paths to all test files
		filenames_list = []
		for (dirpath, _, filenames) in os.walk(path):
			temp_list = [os.path.join(dirpath, name) for name in filenames]
			filenames_list.extend(temp_list)
		return filenames_list

	def test_body_absolute(self):
		filenames_list= self.prep_test_body()
		instance = ipfshttpclient.multipart.FilesStream(filenames_list)
		self.check_test_body(instance, abspath=True)

	def test_body_relative(self):
		filenames_list= self.prep_test_body()

		# Convert absolute paths to relative
		relative_paths_list = [os.path.relpath(cur_path, os.getcwd())
		                       for cur_path in filenames_list]

		instance = ipfshttpclient.multipart.FilesStream(relative_paths_list)
		self.check_test_body(instance, abspath=False)

	def check_test_body(self, instance, abspath):
		expected = r"(--\S+\r\n"
		expected += r"Abspath: \S+\r\n" if abspath else r""
		expected += r"Content-Disposition: file; filename=\"\S+\"\r\n"
		expected += r"Content-Type: application/\S+\r\n"
		expected += r"\r\n(.|\n)*\r\n)+--\S+--\r\n"
		actual = ""
		for i in instance.body():
			if type(i) is not str and type(i) is not memoryview:
				i = i.decode()
			elif six.PY3 and type(i) is memoryview:
				i = i.tobytes().decode()
			actual += i
		assert re.search(expected, actual)


class TestDirectoryStream(unittest.TestCase):
	"""Test the DirectoryStream class.

	Public methods:
	test_body -- check that the HTTP body for the directory is correct
	test_body_recursive -- check body structure when recursive directory
							is uploaded
	"""

	def test_body(self):
		"""Check the multipart HTTP body for the streamed directory."""
		# Get OS-agnostic path to test files
		path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
		                    "functional", "fake_dir")
		instance = ipfshttpclient.multipart.DirectoryStream(path)
		expected = b"^(--\\S+\r\nContent-Disposition: file; filename=\"\\S+\""\
			+ b"\r\nContent-Type: application/\\S+\r\n\r\n(.|\n)*"\
			+ b"\r\n)+--\\S+--\r\n$"
		actual = b"".join(instance.body())
		assert re.search(expected, actual)


class TestBytesFileStream(unittest.TestCase):
	"""Test the TextStream class.

	Public methods:
	test_body -- check that the HTTP body for the text is correct
	"""

	def test_body(self):
		"""Check the multipart HTTP body for the streamed directory."""
		# Get OS-agnostic path to test files
		text = b"Here is some text for this test."
		instance = ipfshttpclient.multipart.BytesFileStream(text)
		expected = b"(--\\S+\r\nContent-Disposition: file; filename=\"\\S+\""\
			+ b"\r\nContent-Type: application/\\S+\r\n"\
			+ b"\r\n(.|\n)*\r\n)+--\\S+--\r\n"
		actual = b"".join(instance.body())
		assert re.search(expected, actual)


class TestStreamHelpers(unittest.TestCase):
	"""Test stream_files, stream_directory, and stream_text.

	TODO: These functions are just wrappers around other,
	already-tested functions. Maybe they should be tested,
	but it is unclear how.

	Public Methods:
	test_stream_files -- unimplemented
	test_stream_directory -- unimplemented
	test_stream_text -- unimplemented
	"""

	def test_stream_files(self):
		"""Test the stream_files function."""
		pass

	def test_stream_directory(self):
		"""Test the stream_directory function."""
		pass

	def test_stream_text(self):
		"""Test the stream_text function."""
		pass
