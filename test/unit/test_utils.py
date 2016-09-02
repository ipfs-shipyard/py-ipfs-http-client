"""Tox unit tests for utils.py.

Classes:
TestUtils -- defines a set of unit tests for untils.py
"""

import io
import json
import os
import pickle
import unittest

import ipfsApi.utils as utils

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
        self.assertEqual(utils.guess_mimetype(path),"text/plain")

    def test_ls_dir(self):
        """Tests utils.ls_dir()

        This test is dependent on the contents of the directory 'fake_dir'
        located in 'test/functional' not being modified.
        """
        path = os.path.join(os.path.dirname(__file__),
                            "..", "functional", "fake_dir")
        dirs = ['test2', 'test3']
        files = ['fsdfgh', 'popoiopiu']
        contents = (files, dirs)
        
        # Sort items before comparing as the ordering of files returned by
        # the file system is not stable
        result = utils.ls_dir(path)
        result[0].sort()
        result[1].sort()
        
        self.assertEqual(result, contents)

    def test_clean_file_opened(self):
        """Tests utils.clean_file() with a stringIO object."""
        string_io = io.StringIO(u'Mary had a little lamb')
        f, opened = utils.clean_file(string_io)
        self.assertEqual(hasattr(f, 'read'), True)
        self.assertEqual(opened, False)
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
        self.assertEqual(hasattr(f, 'read'), True)
        self.assertEqual(opened, True)
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
            self.assertEqual(hasattr(tup[0], 'read'), True)
            self.assertEqual(tup[1], True)
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
            self.assertEqual(hasattr(tup[0], 'read'), True)
            if i == 0:
                self.assertEqual(tup[1], True)
            else:
                self.assertEqual(tup[1], False)
            # Closing files/stringIO objects after test assertions.
            tup[0].close()

    def test_file_size(self):
        """Tests utils.file_size().

        This test relies on the content size of the file 'fsdfgh'
        located in 'test/functional/fake_dir' not being modified.
        """
        path = os.path.join(os.path.dirname(__file__),
                            "..", "functional", "fake_dir", "fsdfgh")
        self.assertEqual(utils.file_size(path), 8)

    def test_return_field_init(self):
        """Tests utils.return_field.__init__()."""
        return_field = utils.return_field('Hash')
        self.assertEqual(return_field.field, 'Hash')

    def test_return_field_call(self):
        """Tests utils.return_field.__call__()."""
        @utils.return_field('Hash')
        def wrapper(string, *args, **kwargs):
            resp = {'Hash':u'QmZfF6C9j4VtoCsTp4KSrhYH47QMd3DNXVZBKaxJdhaPab',
                    'string': string}
            return resp
        self.assertEqual(wrapper('Mary had a little lamb'),
                         u'QmZfF6C9j4VtoCsTp4KSrhYH47QMd3DNXVZBKaxJdhaPab')
