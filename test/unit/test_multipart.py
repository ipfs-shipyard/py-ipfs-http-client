"""Test the file multipart.py

Classes:
TestContentHelpers -- test the three content-header helper functions
TestBodyGenerator -- test the BodyGenerator helper class
TestBufferedGenerator -- test the BufferedGenerator helper class
TestFileStream -- test the FileStream generator class
TestDirectoryStream -- test the DirectoryStream generator class
TestTextStream -- test the TextStream generator class
TestStreamHelpers -- unimplemented
"""

import unittest
import os
import re

import pytest
import six

import ipfsapi.multipart


class TestContentHelpers(unittest.TestCase):
    """Tests the functionality of the three content-oriented helper functions.

    Public methods:
    test_content_disposition -- check the content_disposition defaults
    test_content_disposition_with_type -- check that content_disposition
                                            handles given disposition type
    test_content_type -- check the content_type guessing functionality
    test_multipart_content_type -- check multipart_content_type functionality
    """

    def test_content_disposition(self):
        """Check that content_disposition defaults properly"""
        expected = {'Content-Disposition': 'file; filename="example.txt"'}
        actual = ipfsapi.multipart.content_disposition('example.txt')
        assert expected == actual

    def test_content_disposition_with_type(self):
        """Check that content_disposition handles given disposition type"""
        expected = {'Content-Disposition':
                    'attachment; filename="example.txt"'}
        actual = ipfsapi.multipart.content_disposition('example.txt',
                                                       'attachment')
        assert expected == actual

    def test_content_type(self):
        """Check the content_type guessing functionality."""
        actual = ipfsapi.multipart.content_type('example.txt')
        expected = {'Content-Type': 'text/plain'}
        assert expected == actual

        actual = ipfsapi.multipart.content_type('example.jpeg')
        expected = {'Content-Type': 'image/jpeg'}
        assert expected == actual

        actual = ipfsapi.multipart.content_type('example')
        expected = {'Content-Type': 'application/octet-stream'}
        assert expected == actual

    def test_multipart_content_type(self):
        """Check test_multipart_content_type functionality."""
        actual = ipfsapi.multipart.multipart_content_type(
            '8K5rNKlLQVyreRNncxOTeg')
        expected = {'Content-Type':
                    'multipart/mixed; boundary="8K5rNKlLQVyreRNncxOTeg"'}
        assert expected == actual

        actual = ipfsapi.multipart.multipart_content_type(
            '8K5rNKlLQVyreRNncxOTeg', 'alt')
        expected = {'Content-Type':
                    'multipart/alt; boundary="8K5rNKlLQVyreRNncxOTeg"'}
        assert expected == actual


class TestBodyGenerator(unittest.TestCase):
    """Tests the functionality of the BodyGenerator class.

    Public methods:
    test_init_defaults -- tests the constructor and its behavior with only the
                            required argument
    test_init_with_all -- tests the constructor when all arguments are set
                            explicitly
    test_write_headers -- tests write_headers function against example output
    test_open -- tests open function against example output
    test_file_open -- test file_open function against example output
    test_file_close -- test file_close function against example output
    test_close -- test close function against example output
    """

    def test_init_defaults(self):
        """Test the __init__ function for default parameter values."""
        name = "test_name"
        expected_disposition = 'file; filename="test_name"'
        expected_type = 'multipart/mixed; boundary="\S*"'
        expected_boundary_pattern = '\S*'
        generator = ipfsapi.multipart.BodyGenerator(name)
        assert generator.headers['Content-Disposition'] == expected_disposition
        assert re.search(expected_type,             generator.headers['Content-Type'])
        assert re.search(expected_boundary_pattern, generator.boundary)

    def test_init_with_all(self):
        """Test the __init__ function for explicitly set parameter values."""
        name = "test_name"
        disptype = "test_disp"
        subtype = "test_subtype"
        boundary = "test_boundary"
        generator = ipfsapi.multipart.BodyGenerator(name, disptype,
                                                    subtype, boundary)
        assert generator.headers == {
            'Content-Disposition': 'test_disp; filename="test_name"',
            'Content-Type':
            'multipart/test_subtype; boundary="test_boundary"'}
        assert generator.boundary == boundary

    def test_write_headers(self):
        """Test the write_headers function against sample output."""
        expected = 'Content-Disposition: test_disp; filename="test_name"' \
                   + '\r\nContent-Type: multipart/test_subtype; ' \
                   + 'boundary="test_boundary"\r\n\r\n'
        name = "test_name"
        disptype = "test_disp"
        subtype = "test_subtype"
        boundary = "test_boundary"
        generator = ipfsapi.multipart.BodyGenerator(name, disptype,
                                                    subtype, boundary)
        headers = ""
        for chunk in generator.write_headers():
            if type(chunk) is not str:
                chunk = chunk.decode()
            headers += chunk
        assert headers == expected

    def test_open(self):
        """Test the open function against sample output."""
        expected = '--test_boundary\r\n'
        name = "test_name"
        disptype = "test_disp"
        subtype = "test_subtype"
        boundary = "test_boundary"
        generator = ipfsapi.multipart.BodyGenerator(name, disptype,
                                                    subtype, boundary)
        headers = ""
        for chunk in generator.open():
            if type(chunk) is not str:
                chunk = chunk.decode()
            headers += chunk
        assert headers == expected

    def test_file_open(self):
        """Test the file_open function against sample output."""
        expected = '--test_boundary\r\nContent-Disposition: file; '\
            + 'filename="test_name"\r\nContent-Type: '\
            + 'application/octet-stream\r\n\r\n'
        name = "test_name"
        disptype = "test_disp"
        subtype = "test_subtype"
        boundary = "test_boundary"
        generator = ipfsapi.multipart.BodyGenerator(name, disptype,
                                                    subtype, boundary)
        headers = ""
        for chunk in generator.file_open(name):
            if type(chunk) is not str:
                chunk = chunk.decode()
            headers += chunk
        assert headers == expected

    def test_file_close(self):
        """Test the file_close function against sample output."""
        expected = '\r\n'
        name = "test_name"
        disptype = "test_disp"
        subtype = "test_subtype"
        boundary = "test_boundary"
        generator = ipfsapi.multipart.BodyGenerator(name, disptype,
                                                    subtype, boundary)
        headers = ""
        for chunk in generator.file_close():
            if type(chunk) is not str:
                chunk = chunk.decode()
            headers += chunk
        assert headers == expected

    def test_close(self):
        """Test the close function against sample output."""
        expected = '--test_boundary--\r\n'
        name = "test_name"
        disptype = "test_disp"
        subtype = "test_subtype"
        boundary = "test_boundary"
        generator = ipfsapi.multipart.BodyGenerator(name, disptype,
                                                    subtype, boundary)
        headers = ""
        for chunk in generator.close():
            if type(chunk) is not str:
                chunk = chunk.decode()
            headers += chunk
        assert headers == expected


def _generate_test_chunks(chunk_size, interations):
    """Generates strings of chunk_size length until out of iterations."""
    for i in range(interations):
        output = b""
        for j in range(chunk_size):
            output += b"z"
        yield output


class TestBufferedGenerator(unittest.TestCase):
    """Test the BufferedGenerator class.

    Public methods:
    test_init -- test the default arguments of the constructor
    test_file_chunks -- test the file_chunks function against example output
    test_gen_chunks -- test the gen_chunks function against example output
    test_body -- verify that body is unimplemented
    test_close -- test the close function against example output
    """

    def test_init(self):
        """Test the __init__ function for default parameter values."""
        name = "test_name"
        instance = ipfsapi.multipart.BufferedGenerator(name)
        assert instance.name == name

    def test_file_chunks(self):
        """Test the file_chunks function against example output.

        Warning: This test depends on the contents of
        test/functional/fake_dir/fsdfgh
        Changing that file could break the test.
        """
        name = "fsdfgh"
        chunk_size = 2
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                            "functional", "fake_dir", "fsdfgh")
        instance = ipfsapi.multipart.BufferedGenerator(name, chunk_size)
        expected = 'dsadsad\n'
        output = ""
        open_file = open(path)
        for emitted in instance.file_chunks(open_file):
            if type(emitted) is not str:
                emitted = emitted.decode()
            assert len(emitted) <= chunk_size
            output += emitted
        open_file.close()
        assert output == expected

    def test_gen_chunks(self):
        """Test the gen_chunks function against example output."""
        name = "fsdfgh"
        chunk_size = 2
        instance = ipfsapi.multipart.BufferedGenerator(name, chunk_size)
        for i in instance.gen_chunks(_generate_test_chunks(5, 5)):
            assert len(i) <= chunk_size

    def test_body(self):
        """Ensure that body throws a NotImplemented exception."""
        instance = ipfsapi.multipart.BufferedGenerator("name")
        with pytest.raises(NotImplementedError):
            instance.body()

    def test_close(self):
        """Test the close function against example output."""
        name = "fsdfgh"
        chunk_size = 2
        instance = ipfsapi.multipart.BufferedGenerator(name, chunk_size)
        expected = '--\S+--\r\n'
        actual = ''
        for i in instance.close():
            if type(i) is not str and type(i) is not memoryview:
                i = i.decode()
            elif six.PY3 and type(i) is memoryview:
                i = i.tobytes().decode()
            assert len(i) <= chunk_size
            actual += i

        assert re.search(expected, actual)


class TestFileStream(unittest.TestCase):
    """Test the FileStream class

    Public methods:
    test_body -- check file stream body for proper structure
    """

    def test_body(self):
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
        # Convert absolute paths to relative
        relative_paths_list = [os.path.relpath(cur_path, os.getcwd())
                               for cur_path in filenames_list]

        instance = ipfsapi.multipart.FileStream(relative_paths_list)

        expected = "(--\S+\r\nContent-Disposition: file; filename=\"\S+\""\
            + "\r\nContent-Type: application/\S+\r\n"\
            + "\r\n(.|\n)*\r\n)+--\S+--\r\n"
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
        instance = ipfsapi.multipart.DirectoryStream(path)
        expected = b"^(--\S+\r\nContent-Disposition: form-data; name=\"\S+\"; filename=\"\S+\""\
            + b"\r\nContent-Type: application/\S+\r\n\r\n(.|\n)*"\
            + b"\r\n)+--\S+--\r\n$"
        actual = instance.body()
        """
        for i in instance.body():
            if type(i) is not str and type(i) is not memoryview:
                i = i.decode()
            elif six.PY3 and type(i) is memoryview:
                i = i.tobytes().decode()
            actual += i
        """
        assert re.search(expected, actual)


class TestTextStream(unittest.TestCase):
    """Test the TextStream class.

    Public methods:
    test_body -- check that the HTTP body for the text is correct
    """

    def test_body(self):
        """Check the multipart HTTP body for the streamed directory."""
        # Get OS-agnostic path to test files
        text = "Here is some text for this test."
        instance = ipfsapi.multipart.BytesStream(text)
        expected = "(--\S+\r\nContent-Disposition: file; filename=\"\S+\""\
            + "\r\nContent-Type: application/\S+\r\n"\
            + "\r\n(.|\n)*\r\n)+--\S+--\r\n"
        actual = ""
        for i in instance.body():
            if type(i) is not str and type(i) is not memoryview:
                i = i.decode()
            elif six.PY3 and type(i) is memoryview:
                i = i.tobytes().decode()
            actual += i
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
