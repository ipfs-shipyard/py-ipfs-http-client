"""
Multipart/form-data encoded file streaming.
"""
from __future__ import absolute_import

import fnmatch
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
    """
    Returns a dict containing the MIME content-disposition header for a
    file

    >>> content_disposition('example.txt')
    {'Content-Disposition': 'file; filename="example.txt"'}

    >>> content_disposition('example.txt', 'attachment')
    {'Content-Disposition': 'attachment; filename="example.txt"'}
    """
    disp = '%s; filename="%s"' % (
        disptype,
        quote(fn, safe='')
    )
    return {'Content-Disposition': disp}


def content_type(fn):
    """
    Guesses the mimetype associated with a filename and returns a dict
    containing the content-type header

    >>> content_type('example.txt')
    {'Content-Type': 'text/plain'}

    >>> content_type('example.jpeg')
    {'Content-Type': 'image/jpeg'}

    >>> content_type('example')
    {'Content-Type': 'application/octet-stream'}
    """
    return {'Content-Type': utils.guess_mimetype(fn)}


def multipart_content_type(boundary, subtype='mixed'):
    """
    Returns a dict containing a MIME multipart header with the given
    boundary

    >>> multipart_content_type('8K5rNKlLQVyreRNncxOTeg')
    {'Content-Type': 'multipart/mixed; boundary="8K5rNKlLQVyreRNncxOTeg"'}

    >>> multipart_content_type('8K5rNKlLQVyreRNncxOTeg', 'alt')
    {'Content-Type': 'multipart/alt; boundary="8K5rNKlLQVyreRNncxOTeg"'}
    """
    ctype = 'multipart/%s; boundary="%s"' % (
        subtype,
        boundary
    )
    return {'Content-Type': ctype}


class BodyGenerator(object):
    """
    Generators for multipart/form-data encoding.
    """
    def __init__(self, name, disptype='file', subtype='mixed', boundary=None):

        if boundary is None:
            boundary = self._make_boundary()
        self.boundary = boundary

        headers = content_disposition(name, disptype=disptype)
        headers.update(multipart_content_type(boundary, subtype=subtype))
        self.headers = headers

    def _make_boundary(self):
        return uuid4().hex

    def _write_headers(self, headers):
        if headers:
            for name in sorted(headers.keys()):
                yield name
                yield b': '
                yield headers[name]
                yield CRLF
        yield CRLF

    def write_headers(self):
        for c in self._write_headers(self.headers):
            yield c

    def open(self, **kwargs):
        yield b'--'
        yield self.boundary
        yield CRLF

    def file_open(self, fn):
        yield b'--'
        yield self.boundary
        yield CRLF
        headers = content_disposition(fn)
        headers.update(content_type(fn))
        for c in self._write_headers(headers):
            yield c

    def file_close(self):
        yield CRLF

    def close(self):
        yield b'--'
        yield self.boundary
        yield b'--'
        yield CRLF


class BufferedGenerator(object):

    def __init__(self, name, chunk_size=default_chunk_size):
        """
        An abstract class of buffered generator which encodes
        multipart/form-data.
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
        """
        Yields chunks of a file.
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
        """
        Takes a bytes generator and yields chunks of a maximum of [chunk_size]
        bytes.
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
        raise NotImplemented

    def close(self):
        """
        Closes the multipart envelope.
        """
        for chunk in self.gen_chunks(self.envelope.close()):
            yield chunk


class FileStream(BufferedGenerator):

    def __init__(self, files, chunk_size=default_chunk_size):
        """
        A buffered generator that encodes an array of files as
        multipart/form-data.
        """
        BufferedGenerator.__init__(self, 'files', chunk_size=chunk_size)

        self.files = utils.clean_files(files)

    def body(self):
        for fp, need_close in self.files:
            try:
                name = fp.name
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

    def __init__(self,
                 directory,
                 recursive=False,
                 fnpattern='*',
                 chunk_size=default_chunk_size):
        """
        A buffered generator that encodes a directory as
        multipart/form-data.
        """
        BufferedGenerator.__init__(self, directory, chunk_size=chunk_size)

        self.directory = directory
        self.recursive = recursive
        self.fnpattern = fnpattern

    def body(self, dirname=None, part=None):
        """
        Recursively traverses a directory and generates the multipart encoded
        body.
        """
        if part is None:
            # this is the outer envelope
            outer = True
            part = self.envelope
            dirname = self.directory
        else:
            # this is a an inner mixed part
            outer = False

        if dirname is None:
            dirname = part.name

        for chunk in self.gen_chunks(part.open()):
            yield chunk

        subpart = BodyGenerator(dirname)
        for chunk in self.gen_chunks(subpart.write_headers()):
            yield chunk

        files, subdirs = utils.ls_dir(dirname)

        for fn in files:
            if not fnmatch.fnmatch(fn, self.fnpattern):
                continue
            fullpath = os.path.join(dirname, fn)
            for chunk in self.gen_chunks(subpart.file_open(fullpath)):
                yield chunk
            with open(fullpath, 'rb') as fp:
                for chunk in self.file_chunks(fp):
                    yield chunk
            for chunk in self.gen_chunks(subpart.file_close()):
                yield chunk

        if self.recursive:
            for subdir in subdirs:
                fullpath = os.path.join(dirname, subdir)
                for chunk in self.body(fullpath, subpart):
                    yield chunk

        for chunk in self.gen_chunks(subpart.close()):
            yield chunk

        if outer:
            for chunk in self.close():
                yield chunk


class TextStream(BufferedGenerator):

    def __init__(self, text, chunk_size=default_chunk_size):
        """
        A buffered generator that encodes a string as multipart/form-data.
        """
        BufferedGenerator.__init__(self, 'text', chunk_size=chunk_size)

        self.text = text if isgenerator(text) else (text,)

    def body(self):
        for chunk in self.gen_chunks(self.envelope.file_open(self.name)):
            yield chunk
        for chunk in self.gen_chunks(self.text):
            yield chunk
        for chunk in self.gen_chunks(self.envelope.file_close()):
            yield chunk
        for chunk in self.close():
            yield chunk


def stream_files(files, chunk_size=default_chunk_size):
    """
    Returns a buffered generator which encodes a file or list of files as
    multipart/form-data.  Also returns the corresponding headers.
    """
    stream = FileStream(files, chunk_size=chunk_size)

    return stream.body(), stream.headers


def stream_directory(directory,
                     recursive=False,
                     fnpattern='*',
                     chunk_size=default_chunk_size):
    """
    Returns a buffered generator which encodes a directory as
    multipart/form-data.  Also returns the corresponding headers.
    """
    stream = DirectoryStream(directory,
                             recursive=recursive,
                             fnpattern=fnpattern,
                             chunk_size=chunk_size)

    return stream.body(), stream.headers


def stream_text(text, chunk_size=default_chunk_size):
    """
    Returns a buffered generator which encodes a string as multipart/form-data.
    Also retrns the corresponding headers.
    """
    stream = TextStream(text, chunk_size=chunk_size)

    return stream.body(), stream.headers
