"""
Multipart/form-data encoded file streaming.
"""
from __future__ import absolute_import

import os
from uuid import uuid4

from six.moves.urllib.parse import quote
from six.moves import cStringIO as StringIO
import six

from . import utils

CRLF = '\r\n'


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


def read_in_chunks(fp, chunk_size=1024):
    """
    Reads a file in chunks (defaults to 1kb chunks).
    """
    while True:
        data = fp.read(chunk_size)
        if not data:
            break
        yield data


class MultipartGenerator(object):
    """
    Generators for multipart encoding.
    """
    def __init__(self, headers={}, subtype='mixed', boundary=None):

        if boundary is None:
            boundary = self._make_boundary()
        self.boundary = boundary

        headers.update(multipart_content_type(boundary, subtype=subtype))
        self.headers = headers

    def _make_boundary(self):
        return uuid4().hex

    def _write_headers(self, headers):
        if headers:
            for name in sorted(headers.keys()):
                yield name
                yield ': '
                yield headers[name]
                yield CRLF
        yield CRLF

    def write_headers(self):
        for c in self._write_headers(self.headers):
            yield c

    def open(self, **kwargs):
        yield '--'
        yield self.boundary
        yield CRLF

    def add(self, fn, fp, headers={}, chunk_size=1024):
        yield '--'
        yield self.boundary
        yield CRLF
        headers.update(content_type(fn))
        for c in self._write_headers(headers):
            yield c
        for chunk in read_in_chunks(fp, chunk_size=chunk_size):
            if not isinstance(chunk, six.string_types):
                chunk = chunk.decode('utf-8')
            yield chunk
        yield CRLF

    def close(self):
        yield '--'
        yield self.boundary
        yield '--'
        yield CRLF


class BufferedMultipartGenerator(object):
    """
    A buffered generator which encodes a directory as multipart/form-data.
    """
    def __init__(self, directory, recursive=False, chunk_size=1024):
        self.directory = directory
        self.recursive = recursive
        self.chunk_size = chunk_size

        self.buf = StringIO()
        self.cur = 0

        self.envelope = MultipartGenerator(
            headers=content_disposition(directory, 'form-data'),
            subtype='form-data')

    def gen_chunks(self, gen):
        """
        Yields a chunk when the buffer is full or yields None.
        """
        for data in gen:
            if len(data) < (self.chunk_size - self.cur):
                self.buf.write(data)
                self.cur += len(data)
                yield
            else:
                seek = 0
                while seek < len(data):
                    nb = min((self.chunk_size - self.cur), len(data[seek:]))
                    self.buf.write(data[seek:(seek + nb)])
                    seek += nb
                    self.cur += nb
                    if self.cur == self.chunk_size:
                        self.buf.seek(0)
                        yield self.buf.read(self.chunk_size)
                        self.cur = 0
                        self.buf.seek(0)
                yield

    def generator(self, dirname, part):
        """
        Recursively traverses a directory and generates the multipart encoded
        body.
        """
        for chunk in self.gen_chunks(part.open()):
            if chunk:
                yield chunk

        subpart = MultipartGenerator(headers=content_disposition(dirname))
        for chunk in self.gen_chunks(subpart.write_headers()):
            if chunk:
                yield chunk

        files, subdirs = utils.ls_dir(dirname)

        for fn in files:
            fullpath = os.path.join(dirname, fn)
            with open(fullpath, 'rb') as fp:
                g = subpart.add(fullpath, fp,
                                headers=content_disposition(fullpath),
                                chunk_size=self.chunk_size)
                for chunk in self.gen_chunks(g):
                    if chunk:
                        yield chunk

        if self.recursive:
            for subdir in subdirs:
                fullpath = os.path.join(dirname, subdir)
                for chunk in self.generator(fullpath, subpart):
                    yield chunk

        for chunk in self.gen_chunks(subpart.close()):
            if chunk:
                yield chunk

    def close(self):
        """
        Yields anything left in the buffer and then the closing multipart
        boundary.
        """
        for chunk in self.gen_chunks(self.envelope.close()):
            if chunk:
                yield chunk
        if self.cur > 0:
            self.buf.seek(0)
            yield self.buf.read(self.cur)


def multipart(directory, recursive=False, chunk_size=1024):
    """
    Returns a buffered generator which encodes a directory as
    multipart/form-data.  Also returns the corresponding headers.
    """
    g = BufferedMultipartGenerator(directory,
                                   recursive=recursive,
                                   chunk_size=chunk_size)

    def body(mp_gen, dirname, part):
        for chunk in mp_gen.generator(dirname, part):
            yield chunk
        for chunk in mp_gen.close():
            yield chunk

    return body(g, directory, g.envelope), g.envelope.headers
