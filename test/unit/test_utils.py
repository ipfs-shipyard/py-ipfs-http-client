"""Tox unit tests for utils.py.

Classes:
TestUtils -- defines a set of unit tests for untils.py
"""

import io
import os.path
import unittest

import ipfshttpclient.utils as utils

class TestUtils(unittest.TestCase):
	"""Contains unit tests for utils.py.

	Public methods:
	test_guess_mimetype -- tests utils.guess_mimetype()
	test_ls_dir -- tests utils.ls_dir()
	test_clean_file_opened -- tests utils.clean_file() with a stringIO object
	test_clean_file_unopened -- tests utils.clean_file() with a filepath
	test_clean_files_single -- tests utils.clean_files() with a filepath
	test_clean_files_list -- tests utils.clean_files() with a list of files
	test_file_size -- tests utils.file_size()
	test_return_field_init -- tests utils.return_field.__init__()
	test_return_field_call -- tests utils.return_field.__call__()
	"""
	def test_guess_mimetype(self):
		"""Tests utils.guess_mimetype().

		Guesses the mimetype of the requirements.txt file
		located in the project's root directory.
		"""
		path = os.path.join(os.path.dirname(__file__),
		                    "..", "..", "requirements.txt")
		assert utils.guess_mimetype(path) == "text/plain"

	def test_clean_file_opened(self):
		"""Tests utils.clean_file() with a stringIO object."""
		string_io = io.StringIO(u'Mary had a little lamb')
		f, opened = utils.clean_file(string_io)
		assert hasattr(f, 'read')
		assert not opened
		# Closing stringIO after test assertions.
		f.close()

	def test_clean_file_unopened(self):
		"""Tests utils.clean_file() with a filepath.

		This test relies on the openability of the file 'fsdfgh'
		located in 'test/functional/fake_dir'.
		"""
		path = os.path.join(os.path.dirname(__file__),
		                    "..", "functional", "fake_dir", "fsdfgh")
		f, opened = utils.clean_file(path)
		assert hasattr(f, 'read')
		assert opened
		# Closing file after test assertions.
		f.close()

	def test_clean_files_single(self):
		"""Tests utils.clean_files() with a singular filepath.

		This test relies on the openability of the file 'fsdfgh'
		located in 'test/functional/fake_dir'.
		"""
		path = os.path.join(os.path.dirname(__file__),
		                    "..", "functional", "fake_dir", "fsdfgh")
		gen = utils.clean_files(path)
		for tup in gen:
			assert hasattr(tup[0], 'read')
			assert tup[1]
			# Closing file after test assertions.
			tup[0].close()

	def test_clean_files_list(self):
		"""Tests utils.clean_files() with a list of files/stringIO objects."""
		path = os.path.join(os.path.dirname(__file__),
		                    "..", "functional", "fake_dir", "fsdfgh")
		string_io = io.StringIO(u'Mary had a little lamb')
		files = [path, string_io]
		gen = utils.clean_files(files)
		for i in range(0, 2):
			tup = next(gen)
			assert hasattr(tup[0], 'read')
			if i == 0:
				assert tup[1]
			else:
				assert not tup[1]
			# Closing files/stringIO objects after test assertions.
			tup[0].close()

	def test_return_field_init(self):
		"""Tests utils.return_field.__init__()."""
		return_field = utils.return_field('Hash')
		assert return_field.field == 'Hash'

	def test_return_field_call(self):
		"""Tests utils.return_field.__call__()."""
		expected_hash = u'QmZfF6C9j4VtoCsTp4KSrhYH47QMd3DNXVZBKaxJdhaPab'

		@utils.return_field('Hash')
		def wrapper(string, *args, **kwargs):
			resp = {'Hash': expected_hash, 'string': string}
			return resp
		assert wrapper('Mary had a little lamb') == expected_hash
