"""
Multipart/form-data encoded file streaming.
"""
from __future__ import absolute_import

import os
import fnmatch
from itertools import chain
from uuid import uuid4

from six.moves.urllib.parse import quote
import six

from . import utils


import sys

if sys.version_info < (2, 7):
    # We only support Python 2.6.9+ so any version less than 2.7 will be
    # treated as 2.6 (for testing purposes).
    PY26 = True
else:
    PY26 = False


if PY26:
    # In 2.6 there is no memoryview, so instead I'm just going to use the
    # underlying bytearray, which will end up doing more copying when the
    # bytearray gets sliced.
    memoryview = lambda x: x
else:
    # Trick the py26 pep8 lint tool
    try:
        import builtins
    except ImportError:
        import __builtin__ as builtins
    finally:
        memoryview = builtins.memoryview


CRLF = '\r\n'

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

    def file_open(self, fn):
        yield '--'
        yield self.boundary
        yield CRLF
        headers = content_disposition(fn)
        headers.update(content_type(fn))
        for c in self._write_headers(headers):
            yield c

    def file_close(self):
        yield CRLF

    def close(self):
        yield '--'
        yield self.boundary
        yield '--'
        yield CRLF


class BufferedGenerator(object):

    def __init__(self, name, chunk_size=default_chunk_size):
        """
        An abstract class of buffered generator which encodes
        multipart/form-data.
        """
        self.chunk_size = chunk_size
        self._buf = bytearray(chunk_size)

        # handle manipulation of buffer throught a memoryview.
        #   This allows us to write from a file directly to a buffer at any
        #   given offset.
        self.buf = memoryview(self._buf)
        self.cur = 0

        self.name = name
        self.envelope = BodyGenerator(self.name,
                                      disptype='form-data',
                                      subtype='form-data')
        self.headers = self.envelope.headers

    def file_chunks(self, fp):
        """
        Yields chunks of a file when the buffer is full else yields None.
        """
        # get filesize from file object
        fp.seek(0, 2)
        fsize = fp.tell()
        fp.seek(0)

        offset = 0
        while offset < fsize:
            try:
                if PY26:
                    raise AttributeError
                nb = fp.readinto(self.buf[self.cur:])
            except AttributeError:
                nb = min(self.chunk_size - self.cur, fsize - offset)
                ch = fp.read(nb)
                if not isinstance(ch, six.binary_type):
                    ch = ch.encode('utf-8')
                self.buf[self.cur:self.cur + nb] = ch
            offset += nb
            self.cur += nb
            if self.cur == self.chunk_size:
                yield self.buf
                self.cur = 0
        yield

    def gen_chunks(self, gen):
        """
        Takes a bytes generator and feeds it into the internal buffer. Yields a
        chunk when the buffer is full or yields None.
        """
        for data in gen:
            if not isinstance(data, six.binary_type):
                data = data.encode('utf-8')
            mv = memoryview(data)
            size = len(mv)
            offset = 0
            while offset < size:
                nb = min(self.chunk_size - self.cur, size - offset)
                self.buf[self.cur:self.cur + nb] = mv[offset:offset + nb]
                offset += nb
                self.cur += nb
                if self.cur == self.chunk_size:
                    yield self.buf
                    self.cur = 0
            yield

    def body(self, *args, **kwargs):
        raise NotImplemented

    def close(self):
        """
        Yields anything left in the buffer and then the closing multipart
        boundary.
        """
        for chunk in self.gen_chunks(self.envelope.close()):
            if chunk:
                yield chunk
        if self.cur > 0:
            yield self.buf[:self.cur]


class FileStream(BufferedGenerator):

    def __init__(self, _file, chunk_size=default_chunk_size):
        """
        A buffered generator that encodes a single file as
        multipart/form-data.
        """
        self.fileobj, self._need_close = utils.clean_file(_file)
        try:
            name = self.fileobj.name
        except AttributeError:
            name = 'file'
        BufferedGenerator.__init__(self, name, chunk_size=chunk_size)

    def body(self):
        for chunk in self.gen_chunks(self.envelope.file_open(self.name)):
            if chunk:
                yield chunk
        for chunk in self.file_chunks(self.fileobj):
            if chunk:
                yield chunk
        for chunk in self.gen_chunks(self.envelope.file_close()):
            if chunk:
                yield chunk
        if self._need_close:
            self.fileobj.close()


class MultipleFileStream(BufferedGenerator):

    def __init__(self, files, chunk_size=default_chunk_size):
        """
        A buffered generator that encodes an array of files as
        multipart/form-data.
        """
        BufferedGenerator.__init__(self, 'files', chunk_size=chunk_size)

        # get clean list of file objects
        #   This is a list of tuples, where the first element is the file
        #   object and the second element is a boolean which is True is this
        #   module opened the file (and thus should close it).
        self.fileobjs = utils.clean_files(files)

    def body(self):
        for fp, need_close in self.fileobjs:
            try:
                name = fp.name
            except AttributeError:
                name = ''
            for chunk in self.gen_chunks(self.envelope.file_open(name)):
                if chunk:
                    yield chunk
            for chunk in self.file_chunks(fp):
                if chunk:
                    yield chunk
            for chunk in self.gen_chunks(self.envelope.file_close()):
                if chunk:
                    yield chunk
            if need_close:
                fp.close()


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
            part = self.envelope
            dirname = self.directory
        if dirname is None:
            dirname = ''

        for chunk in self.gen_chunks(part.open()):
            if chunk:
                yield chunk

        subpart = BodyGenerator(dirname)
        for chunk in self.gen_chunks(subpart.write_headers()):
            if chunk:
                yield chunk

        files, subdirs = utils.ls_dir(dirname)

        for fn in files:
            if not fnmatch.fnmatch(fn, self.fnpattern):
                continue
            fullpath = os.path.join(dirname, fn)
            for chunk in self.gen_chunks(subpart.file_open(fullpath)):
                if chunk:
                    yield chunk
            with open(fullpath, 'rb') as fp:
                for chunk in self.file_chunks(fp):
                    if chunk:
                        yield chunk
            for chunk in self.gen_chunks(subpart.file_close()):
                if chunk:
                    yield chunk

        if self.recursive:
            for subdir in subdirs:
                fullpath = os.path.join(dirname, subdir)
                for chunk in self.body(fullpath, subpart):
                    yield chunk

        for chunk in self.gen_chunks(subpart.close()):
            if chunk:
                yield chunk


def stream_file(fileobj, chunk_size=default_chunk_size):
    """
    Returns a buffered generator which encodes a file as multipart/form-data.
    Also returns the corresponding headers.
    """
    stream = FileStream(fileobj, chunk_size=chunk_size)

    return chain(stream.body(), stream.close()), stream.headers


def stream_files(files, chunk_size=default_chunk_size):
    """
    Returns a buffered generator which encodes a list of files as
    multipart/form-data.  Also returns the corresponding headers.
    """
    stream = MultipleFileStream(files, chunk_size=chunk_size)

    return chain(stream.body(), stream.close()), stream.headers


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

    return chain(stream.body(), stream.close()), stream.headers
