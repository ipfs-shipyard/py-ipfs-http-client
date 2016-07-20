"""HTTP Multipart/* encoded file streaming.

Classes:
BodyGenerator -- generates the body of an HTTP-encoded multipart request
BufferedGenerator -- abstract class that generates the wrapper around HTTP
                        multipart bodies
FileStream -- generates the HTTP multipart request body for a group of files
DirectoryStream -- generates the HTTP multipart request body for a directory
TextStream -- generates the HTTP multipart request body for a chunk of text

Functions:
content_disposition -- returns a dict containing the MIME content-disposition
                        header for a file
content_type -- returns a dict with the content-type header for a file
multipart_content_type -- creates a MIME multipart header with the given
                            configuration
stream_files -- gets a buffered generator for streaming files
stream_directory -- gets a buffered generator for streaming directories
stream_text -- gets a buffered generator for streaming text
"""
from __future__ import absolute_import

import fnmatch
import requests
import io
import os
from inspect import isgenerator
from sys import version_info
from uuid import uuid4

import six

from six.moves.urllib.parse import quote

from . import utils

if version_info > (3,):
    from builtins import memoryview as buffer


CRLF = b'\r\n'

default_chunk_size = 4096


def content_disposition(fn, disptype='file'):
    """Returns a dict containing the MIME content-disposition header for a file.

    Example:
    >>> content_disposition('example.txt')
    {'Content-Disposition': 'file; filename="example.txt"'}

    >>> content_disposition('example.txt', 'attachment')
    {'Content-Disposition': 'attachment; filename="example.txt"'}

    Keyword arguments:
    fn -- filename to retrieve the MIME content-disposition for
    disptype -- the disposition type to use for the file
    """
    disp = '%s; filename="%s"' % (
        disptype,
        quote(fn, safe='')
    )
    return {'Content-Disposition': disp}


def content_type(fn):
    """Returns a dict with the content-type header for a file.

    Guesses the mimetype for a filename and returns a dict
    containing the content-type header.

    Example:
    >>> content_type('example.txt')
    {'Content-Type': 'text/plain'}

    >>> content_type('example.jpeg')
    {'Content-Type': 'image/jpeg'}

    >>> content_type('example')
    {'Content-Type': 'application/octet-stream'}

    Keyword Arguments:
    fn -- filename to guess the content-type for
    """
    return {'Content-Type': utils.guess_mimetype(fn)}


def multipart_content_type(boundary, subtype='mixed'):
    """Creates a MIME multipart header with the given configuration.

    Returns a dict containing a MIME multipart header with the given
    boundary.

    Example:
    >>> multipart_content_type('8K5rNKlLQVyreRNncxOTeg')
    {'Content-Type': 'multipart/mixed; boundary="8K5rNKlLQVyreRNncxOTeg"'}

    >>> multipart_content_type('8K5rNKlLQVyreRNncxOTeg', 'alt')
    {'Content-Type': 'multipart/alt; boundary="8K5rNKlLQVyreRNncxOTeg"'}

    Keyword arguments:
    boundary -- the boundary size to put in the header
    subtype -- the MIME subtype to put in the header
    """
    ctype = 'multipart/%s; boundary="%s"' % (
        subtype,
        boundary
    )
    return {'Content-Type': ctype}


class BodyGenerator(object):
    """Generators for creating the body of a multipart/* HTTP request.

    Instance variables:
    boundary -- a separator for the body chunk being generated
    headers -- the headers of the body chunk being generated

    Public methods:
    __init__ -- create a BodyGenerator
    write_headers -- generator that yields HTTP headers for content
    open -- generator that opens a body section for content
    file_open -- generator that opens a file section for content
    file_close -- generator that closes a file section for content
    close -- generator that closes a body section for content
    """

    def __init__(self, name, disptype='file', subtype='mixed', boundary=None):
        """Create a BodyGenerator.

        Keyword arguments:
        name -- the name of the file(s)/content being encoded
        disptype -- the content-disposition of the content
        subtype -- the HTTP multipart/<subtype> type of the content
        boundary -- an identifier for the body being generated
        """
        # If the boundary is unspecified, make a random one
        if boundary is None:
            boundary = self._make_boundary()
        self.boundary = boundary

        headers = content_disposition(name, disptype=disptype)
        headers.update(multipart_content_type(boundary, subtype=subtype))
        self.headers = headers

    def _make_boundary(self):
        """Returns a random hexadecimal string (UUID 4).

        The HTTP multipart request body spec requires a boundary string to
        separate different content chunks within a request, and this is
        usually a random string. Using a UUID is an easy way to generate
        a random string of appropriate length as this content separator.
        """
        return uuid4().hex

    def _write_headers(self, headers):
        """Generator function that yields the HTTP header for content.

        Keyword arguments:
        headers -- the dictionary of headers to yield
        """
        if headers:
            for name in sorted(headers.keys()):
                yield name
                yield b': '
                yield headers[name]
                yield CRLF
        yield CRLF

    def write_headers(self):
        """Generator function that writes out the HTTP headers for content."""
        for c in self._write_headers(self.headers):
            yield c

    def open(self, **kwargs):
        """Generator function that opens a body section for content.

        Keyword arguments:
        kwargs -- keyword arguments, unused
        """
        yield b'--'
        yield self.boundary
        yield CRLF

    def file_open(self, fn):
        """Generator function that opens a file section in multipart HTTP.

        Keyword arguments:
        fn -- filename for the file being opened and added to the HTTP
                body
        """
        yield b'--'
        yield self.boundary
        yield CRLF
        headers = content_disposition(fn)
        headers.update(content_type(fn))
        for c in self._write_headers(headers):
            yield c

    def file_close(self):
        """Generator function that ends a file section in HTTP encoding."""
        yield CRLF

    def close(self):
        """Generator function that ends a content area in an HTTP body."""
        yield b'--'
        yield self.boundary
        yield b'--'
        yield CRLF


class BufferedGenerator(object):
    """Generator that encodes multipart/form-data.

    An abstract class of buffered generator which encodes
    multipart/form-data.

    Instance variables:
    chunk_size -- the maximum size of a generated chunk of a file
    buf -- buffer containing the current file chunk
    name -- the name of the file being chunked
    envelope -- a BodyGenerator to wrap the chunked content
    headers -- the HTTP multipart headers for the chunked content

    Public methods:
    __init__ -- generator that encodes multipart/form-data
    file_chunks -- yields chunks of a file
    gen_chunks -- generates byte chunks of a given size
    body -- returns the body of the buffered file
    close -- closes the multipart envelope
    """

    def __init__(self, name, chunk_size=default_chunk_size):
        """Generator that encodes multipart/form-data.

        An abstract class of buffered generator which encodes
        multipart/form-data.

        Keyword arguments:
        name -- the name of the file to encode
        chunk_size -- the maxiumum size for any chunk in bytes
        """
        self.chunk_size = chunk_size
        self._internal = bytearray(chunk_size)
        self.buf = buffer(self._internal)

        self.name = name
        self.envelope = BodyGenerator(self.name,
                                      disptype='form-data',
                                      subtype='form-data')
        self.headers = self.envelope.headers

    def file_chunks(self, fp):
        """Yields chunks of a file.

        Keyword arguments:
        fp -- the file to break into chunks (must be an open file or have the
                readinto method)
        """
        fsize = utils.file_size(fp)
        offset = 0
        if hasattr(fp, 'readinto'):
            while offset < fsize:
                nb = fp.readinto(self._internal)
                yield self.buf[:nb]
                offset += nb
        else:
            while offset < fsize:
                nb = min(self.chunk_size, fsize - offset)
                yield fp.read(nb)
                offset += nb

    def gen_chunks(self, gen):
        """Generates byte chunks of a given size.

        Takes a bytes generator and yields chunks of a maximum of [chunk_size]
        bytes.

        Keyword arguments:
        gen -- the bytes generator that produces the bytes
        """
        for data in gen:
            if not isinstance(data, six.binary_type):
                data = data.encode('utf-8')
            size = len(data)
            if size < self.chunk_size:
                yield data
            else:
                mv = buffer(data)
                offset = 0
                while offset < size:
                    nb = min(self.chunk_size, size - offset)
                    yield mv[offset:offset + nb]
                    offset += nb

    def body(self, *args, **kwargs):
        """Returns the body of the buffered file.

        Warning: this function is not implemented.

        Keyword arguments:
        args -- additional arguments, unused
        kwargs -- additional keyword arguments, unused
        """
        raise NotImplementedError

    def close(self):
        """Closes the multipart envelope."""
        for chunk in self.gen_chunks(self.envelope.close()):
            yield chunk


class FileStream(BufferedGenerator):
    """Generator that encodes multiples files into HTTP multipart.

    A buffered generator that encodes an array of files as
    multipart/form-data. This is a concrete implementation of
    BufferedGenerator.

    Instance variables:
    files -- array of files to be encoded

    Public methods:
    __init__ -- creates a new FileStream
    body -- generate the HTTP multipart-encoded body
    """

    def __init__(self, files, chunk_size=default_chunk_size):
        """Creates a new FileStream.

        A buffered generator that encodes an array of files as
        multipart/form-data.

        Keyword arguments:
        name -- the name of the file to encode
        chunk_size -- the maxiumum size for any chunk in bytes
        """
        BufferedGenerator.__init__(self, 'files', chunk_size=chunk_size)

        self.files = utils.clean_files(files)

    def body(self):
        """Returns the body of the buffered file."""
        for fp, need_close in self.files:
            try:
                name = os.path.basename(fp.name)
            except AttributeError:
                name = ''
            for chunk in self.gen_chunks(self.envelope.file_open(name)):
                yield chunk
            for chunk in self.file_chunks(fp):
                yield chunk
            for chunk in self.gen_chunks(self.envelope.file_close()):
                yield chunk
            if need_close:
                fp.close()
        for chunk in self.close():
            yield chunk


class DirectoryStream(BufferedGenerator):
    """Generator that encodes a director into HTTP multipart.

    A buffered generator that encodes a directory as
    multipart/form-data.

    Instance variables:
    directory -- the directory being encoded
    recursive -- whether or not to recursively encode directory contents
    fnpattern -- a pattern to match filenames (if no match, file is excluded)
    headers -- the HTTP headers for uploading self.directory (included for
                external API consistency)

    Public methods:
    __init__ -- creates a new FileStream
    body -- returns the HTTP body for this directory upload request
    headers -- returns the HTTP headers for this directory upload request
    """

    def __init__(self,
                 directory,
                 recursive=False,
                 fnpattern='*',
                 chunk_size=default_chunk_size):
        """A buffered generator that encodes a directory as multipart/form-data.

        Keyword arguments:
        directory -- the directory to encode
        chunk_size -- the maximum size of a file chunk to use
        """
        BufferedGenerator.__init__(self, directory, chunk_size=chunk_size)

        self.directory = directory
        self.recursive = recursive
        self.fnpattern = fnpattern
        self._request = self._prepare()
        self.headers = self._request.headers

    def body(self):
        """Returns the HTTP headers for this directory upload request."""
        return self._request.body

    def headers(self):
        """Returns the HTTP body for this directory upload request."""
        return self._request.headers

    def _prepare(self):
        """Pre-formats the multipart HTTP request to transmit the directory."""
        names = []
        # identify the unecessary portion of the relative path
        truncate = os.path.dirname(self.directory)
        # traverse the filesystem downward from the target directory's uri
        for curr_dir, _, files in os.walk(self.directory):
            # find the path relative to the directory being added
            if len(truncate) > 0:
                _, _, short_path = curr_dir.partition(truncate)
            else:
                short_path = curr_dir
            # remove leading / or \ if it is present
            if short_path.startswith(os.sep):
                short_path = short_path[1:]
            # create an empty, fake file to represent the directory
            mock_file = io.StringIO()
            mock_file.write(u'')
            # add this file to those that will be sent
            names.append(('files', (short_path, mock_file, 'application/x-directory')))
            # iterate across the files in the current directory
            for filename in files:
                # find the name of the file relative to the directory being added
                short_name = os.path.join(short_path, filename)
                filepath = os.path.join(curr_dir, filename)
                # remove leading / or \ if it is present
                if short_name.startswith(os.sep):
                    short_name = short_name[1:]
                # add the file to those being sent
                names.append(('files', (short_name, open(filepath, 'rb'), 'application/octet-stream')))
        # send the request and present the response body to the user
        req = requests.Request("POST", 'http://localhost', files=names)
        prep = req.prepare()
        return prep


class TextStream(BufferedGenerator):
    """A buffered generator that encodes a string as multipart/form-data.

    Instance variables:
    text -- the text to stream

    Public methods:
    __init__ -- create a TextStream
    body -- generator that yields the encoded body
    """

    def __init__(self, text, chunk_size=default_chunk_size):
        """A buffered generator that encodes a string as multipart/form-data.

        Keyword arguments:
        text -- the text to stream
        chunk_size -- maximum size of a single data chunk
        """
        BufferedGenerator.__init__(self, 'text', chunk_size=chunk_size)

        self.text = text if isgenerator(text) else (text,)

    def body(self):
        """Generator that yields the encoded body."""
        for chunk in self.gen_chunks(self.envelope.file_open(self.name)):
            yield chunk
        for chunk in self.gen_chunks(self.text):
            yield chunk
        for chunk in self.gen_chunks(self.envelope.file_close()):
            yield chunk
        for chunk in self.close():
            yield chunk


def stream_files(files, chunk_size=default_chunk_size):
    """Gets a buffered generator for streaming files.

    Returns a buffered generator which encodes a file or list of files as
    multipart/form-data.  Also returns the corresponding headers.

    Keyword arguments:
    files -- the file(s) to stream
    chunk_size -- maxiumum size of each stream chunk
    """
    stream = FileStream(files, chunk_size=chunk_size)

    return stream.body(), stream.headers


def stream_directory(directory,
                     recursive=False,
                     fnpattern='*',
                     chunk_size=default_chunk_size):
    """Gets a buffered generator for streaming directories.

    Returns a buffered generator which encodes a directory as
    multipart/form-data.  Also returns the corresponding headers.

    Keyword arguments:
    directory -- the directory to stream
    recursive -- boolean, True to stream all content recursively
    fnpattern -- pattern of filenames to keep, functions like filter
    chunk_size -- maximum size of each stream chunk
    """
    stream = DirectoryStream(directory,
                             recursive=recursive,
                             fnpattern=fnpattern,
                             chunk_size=chunk_size)

    return stream.body(), stream.headers


def stream_text(text, chunk_size=default_chunk_size):
    """Gets a buffered generator for streaming text.

    Returns a buffered generator which encodes a string as multipart/form-data.
    Also retrns the corresponding headers.

    Keyword arguments:
    text -- the text to stream
    chunk_size -- the maximum size of each stream chunk
    """
    stream = TextStream(text, chunk_size=chunk_size)

    return stream.body(), stream.headers
