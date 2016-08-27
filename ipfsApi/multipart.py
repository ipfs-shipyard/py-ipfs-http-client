"""HTTP :mimetype:`multipart/*`-encoded file streaming.
"""
from __future__ import absolute_import

# import fnmatch
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

    .. code-block:: python

        >>> content_disposition('example.txt')
        {'Content-Disposition': 'file; filename="example.txt"'}

        >>> content_disposition('example.txt', 'attachment')
        {'Content-Disposition': 'attachment; filename="example.txt"'}

    Parameters
    ----------
    fn : str
        Filename to retrieve the MIME content-disposition for
    disptype : str
        Rhe disposition type to use for the file
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

    .. code-block:: python

        >>> content_type('example.txt')
        {'Content-Type': 'text/plain'}

        >>> content_type('example.jpeg')
        {'Content-Type': 'image/jpeg'}

        >>> content_type('example')
        {'Content-Type': 'application/octet-stream'}

    Parameters
    ----------
    fn : str
        Filename to guess the content-type for
    """
    return {'Content-Type': utils.guess_mimetype(fn)}


def multipart_content_type(boundary, subtype='mixed'):
    """Creates a MIME multipart header with the given configuration.

    Returns a dict containing a MIME multipart header with the given
    boundary.

    .. code-block:: python

        >>> multipart_content_type('8K5rNKlLQVyreRNncxOTeg')
        {'Content-Type': 'multipart/mixed; boundary="8K5rNKlLQVyreRNncxOTeg"'}

        >>> multipart_content_type('8K5rNKlLQVyreRNncxOTeg', 'alt')
        {'Content-Type': 'multipart/alt; boundary="8K5rNKlLQVyreRNncxOTeg"'}

    Parameters
    ----------
    boundry : str
        The content delimiter to put into the header
    subtype : str
        The subtype in :mimetype:`multipart/*`-domain to put into the header
    """
    ctype = 'multipart/%s; boundary="%s"' % (
        subtype,
        boundary
    )
    return {'Content-Type': ctype}


class BodyGenerator(object):
    """Generators for creating the body of a :mimetype:`multipart/*`
    HTTP request.

    Parameters
    ----------
    name : str
        The filename of the file(s)/content being encoded
    disptype : str
        The ``Content-Disposition`` of the content
    subtype : str
        The :mimetype:`multipart/*`-subtype of the content
    boundary : str
        An identifier used as a delimiter for the content's body
    """

    def __init__(self, name, disptype='file', subtype='mixed', boundary=None):
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
        """Yields the HTTP header text for some content.

        Parameters
        ----------
        headers : dict
            The headers to yield
        """
        if headers:
            for name in sorted(headers.keys()):
                yield name
                yield b': '
                yield headers[name]
                yield CRLF
        yield CRLF

    def write_headers(self):
        """Yields the HTTP header text for the content."""
        for c in self._write_headers(self.headers):
            yield c

    def open(self, **kwargs):
        """Yields the body section for the content.
        """
        yield b'--'
        yield self.boundary
        yield CRLF

    def file_open(self, fn):
        """Yields the opening text of a file section in multipart HTTP.

        Parameters
        ----------
        fn : str
            Filename for the file being opened and added to the HTTP body
        """
        yield b'--'
        yield self.boundary
        yield CRLF
        headers = content_disposition(fn)
        headers.update(content_type(fn))
        for c in self._write_headers(headers):
            yield c

    def file_close(self):
        """Yields the end text of a file section in HTTP multipart encoding."""
        yield CRLF

    def close(self):
        """Yields the ends of the content area in a HTTP multipart body."""
        yield b'--'
        yield self.boundary
        yield b'--'
        yield CRLF


class BufferedGenerator(object):
    """Generator that encodes multipart/form-data.

    An abstract buffered generator class which encodes
    :mimetype:`multipart/form-data`.

    Parameters
    ----------
    name : str
        The name of the file to encode
    chunk_size : int
        The maximum size that any single file chunk may have in bytes
    """

    def __init__(self, name, chunk_size=default_chunk_size):
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

        Parameters
        ----------
        fp : io.RawIOBase
            The file to break into chunks
            (must be an open file or have the ``readinto`` method)
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

        Takes a bytes generator and yields chunks of a maximum of
        ``chunk_size`` bytes.

        Parameters
        ----------
        gen : generator
            The bytes generator that produces the bytes
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

        .. note:: This function is not actually implemented.
        """
        raise NotImplementedError

    def close(self):
        """Yields the closing text of a multipart envelope."""
        for chunk in self.gen_chunks(self.envelope.close()):
            yield chunk


class FileStream(BufferedGenerator):
    """Generator that encodes multiples files into HTTP multipart.

    A buffered generator that encodes an array of files as
    :mimetype:`multipart/form-data`. This is a concrete implementation of
    :class:`~ipfsApi.multipart.BufferedGenerator`.

    Parameters
    ----------
    name : str
        The filename of the file to encode
    chunk_size : int
        The maximum size that any single file chunk may have in bytes
    """

    def __init__(self, files, chunk_size=default_chunk_size):
        BufferedGenerator.__init__(self, 'files', chunk_size=chunk_size)

        self.files = utils.clean_files(files)

    def body(self):
        """Yields the body of the buffered file."""
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
    """Generator that encodes a directory into HTTP multipart.

    A buffered generator that encodes an array of files as
    :mimetype:`multipart/form-data`. This is a concrete implementation of
    :class:`~ipfsApi.multipart.BufferedGenerator`.

    Parameters
    ----------
    directory : str
        The filepath of the directory to encode
    chunk_size : int
        The maximum size that any single file chunk may have in bytes
    """

    def __init__(self,
                 directory,
                 recursive=False,
                 fnpattern='*',
                 chunk_size=default_chunk_size):
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
        if self.directory.endswith(os.sep):
            self.directory = self.directory[:-1]
        # identify the unecessary portion of the relative path
        truncate = os.path.dirname(self.directory)
        # traverse the filesystem downward from the target directory's uri
        # Errors: `os.walk()` will simply return an empty generator if the
        # target directory does not exist.
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
            names.append(('files',
                         (short_path, mock_file, 'application/x-directory')))
            # iterate across the files in the current directory
            for filename in files:
                # find the filename relative to the directory being added
                short_name = os.path.join(short_path, filename)
                filepath = os.path.join(curr_dir, filename)
                # remove leading / or \ if it is present
                if short_name.startswith(os.sep):
                    short_name = short_name[1:]
                # add the file to those being sent
                names.append(('files', (short_name,
                                        open(filepath, 'rb'),
                                        'application/octet-stream')))
        # send the request and present the response body to the user
        req = requests.Request("POST", 'http://localhost', files=names)
        prep = req.prepare()
        return prep


class TextStream(BufferedGenerator):
    """A buffered generator that encodes a string as
    :mimetype:`multipart/form-data`.

    Parameters
    ----------
    text : str
        The text to stream to the daemon
    chunk_size : int
        The maximum size of a single data chunk
    """

    def __init__(self, text, chunk_size=default_chunk_size):
        BufferedGenerator.__init__(self, 'text', chunk_size=chunk_size)

        self.text = text if isgenerator(text) else (text,)

    def body(self):
        """Yields the encoded body."""
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
    :mimetype:`multipart/form-data` with the corresponding headers.

    Parameters
    ----------
    files : str
        The file(s) to stream
    chunk_size : int
        Maximum size of each stream chunk
    """
    stream = FileStream(files, chunk_size=chunk_size)

    return stream.body(), stream.headers


def stream_directory(directory,
                     recursive=False,
                     fnpattern='*',
                     chunk_size=default_chunk_size):
    """Gets a buffered generator for streaming directories.

    Returns a buffered generator which encodes a directory as
    :mimetype:`multipart/form-data` with the corresponding headers.

    Parameters
    ----------
    directory : str
        The filename of the directory to stream
    recursive : bool
        Stream all content within the directory recursively?
    fnpattern : str
        *fnmatch* pattern of filenames to keep
    chunk_size : int
        Maximum size of each stream chunk
    """
    stream = DirectoryStream(directory,
                             recursive=recursive,
                             fnpattern=fnpattern,
                             chunk_size=chunk_size)

    return stream.body(), stream.headers


def stream_text(text, chunk_size=default_chunk_size):
    """Gets a buffered generator for streaming text.

    Returns a buffered generator which encodes a string as
    :mimetype:`multipart/form-data` with the corresponding headers.

    Parameters
    ----------
    text : str
        The text to stream
    chunk_size : int
        The maximum size of each stream chunk
    """
    stream = TextStream(text, chunk_size=chunk_size)

    return stream.body(), stream.headers
