"""
Streaming Multipart Encoded Files
=================================

**NOTE: This is temporary until we can fork python-requests and/or urllib3 to
        provide the same functionality.
"""
from __future__ import absolute_import

import os
import fnmatch
from uuid import uuid4

from six.moves.urllib.parse import quote
from six.moves import cStringIO as StringIO
import six

from . import utils

CRLF = '\r\n'


def content_disposition(fn, disptype='file'):
    disp = '%s; filename="%s"' % (
        disptype,
        quote(fn, safe='')
    )
    return {'Content-Disposition': disp}


def content_type(fn):
    return {'Content-Type': utils.guess_mimetype(fn)}


def multipart_content_type(boundary, subtype='mixed'):
    ctype = 'multipart/%s; boundary="%s"' % (
        subtype,
        boundary
    )
    return {'Content-Type': ctype}


class MultipartWriter(object):

    def __init__(self, buf, headers={}, subtype='mixed', boundary=None):
        self.buf = buf

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
                self.buf.write(name)
                self.buf.write(': ')
                self.buf.write(headers[name])
                self.buf.write(CRLF)
        self.buf.write(CRLF)

    def write_headers(self):
        self._write_headers(self.headers)

    def open(self, **kwargs):
        self.buf.write('--')
        self.buf.write(self.boundary)
        self.buf.write(CRLF)
        return MultipartWriter(self.buf, **kwargs)

    def add(self, fn, content, headers={}):
        self.buf.write('--')
        self.buf.write(self.boundary)
        self.buf.write(CRLF)
        headers.update(content_type(fn))
        self._write_headers(headers)
        if content:
            if not isinstance(content, six.string_types):
                content = content.decode('utf-8')
            self.buf.write(content)
            self.buf.write(CRLF)

    def close(self):
        self.buf.write('--')
        self.buf.write(self.boundary)
        self.buf.write('--')
        self.buf.write(CRLF)


#
# TURN THIS INTO A CLASS WHERE YOU OVERWRITE METHODS THAT ARE TRIGGERED WHEN
# YOU ENTER AND EXIT A SUBDIRECTORY
#
def walk(dirname, fnpattern='*', recursive=False):
    """
    Generator that walks a directory (optionally recursive).
    """
    yield dirname, False

    files, subdirs = utils.ls_dir(dirname)

    for fn in files:
        if not fnmatch.fnmatch(fn, fnpattern):
            continue
        yield os.path.join(dirname, fn), True

    if recursive:
        for sd in subdirs:
            for result in walk(os.path.join(dirname, sd), recursive=True):
                yield result


def recursive(dirname, fnpattern='*'):
    """
    Python-requests can supports chunked output by passing a generator to
    the [data] keyword arg in the request api.  This should be a chunked
    generator... eventually.

    TODO: transform this into a generator for chunked file output
    """

    # this should really be a io.BufferedWriter or something
    buf = StringIO()

    def walk(dirname, part):
        subpart = part.open(headers=content_disposition(dirname))
        subpart.write_headers()

        files, subdirs = utils.ls_dir(dirname)

        for fn in files:
            if not fnmatch.fnmatch(fn, fnpattern):
                continue
            fullpath = os.path.join(dirname, fn)
            with open(fullpath, 'rb') as fp:
                subpart.add(fullpath,
                            fp.read(),
                            headers=content_disposition(fullpath))

        for subdir in subdirs:
            fullpath = os.path.join(dirname, subdir)
            walk(fullpath, subpart)

        subpart.close()
        return

    envelope = MultipartWriter(
        buf,
        headers=content_disposition(dirname, 'form-data'),
        subtype='form-data')

    walk(dirname, envelope)

    envelope.close()

    return buf.getvalue(), envelope.headers
