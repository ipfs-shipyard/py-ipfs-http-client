"""
Streaming Multipart Encoded Files
=================================

**NOTE: This is temporary until we can fork python-requests and/or urllib3 to
        provide the same functionality.
"""
import os
import fnmatch
from urllib import quote
from uuid import uuid4
from cStringIO import StringIO

from . import utils


CRLF = '\r\n'

class MultipartWriter(object):

    def __init__(self, buf, headers={}, subtype='mixed', boundary=None):
        self.buf = buf
        
        if boundary is None:
            boundary = self._make_boundary()
        self.boundary = boundary
        
        headers['Content-Type'] = 'multipart/%s; boundary="%s"' % (
            subtype,
            self.boundary
        )
        self.headers = headers

    def open(self, **kwargs):
        self.buf.write('--')
        self.buf.write(self.boundary)
        self.buf.write(CRLF)
        return MultipartWriter(self.buf, **kwargs)

    def add(self, fn, content, headers={}):
        self.buf.write('--')
        self.buf.write(self.boundary)
        self.buf.write(CRLF)

        headers['Content-Type'] = utils.guess_mimetype(fn)

        self._write_headers(headers)
        if content:
            self.buf.write(content)
            self.buf.write(CRLF)

    def close(self):
        self.buf.write('--')
        self.buf.write(self.boundary)
        self.buf.write('--')
        self.buf.write(CRLF)

    def _make_boundary(self):
        return uuid4().hex

    def write_headers(self):
        self._write_headers(self.headers)

    def _write_headers(self, headers):
        if headers:
            for name in sorted(headers.keys()):
                self.buf.write(name)
                self.buf.write(': ')
                self.buf.write(headers[name])
                self.buf.write(CRLF)
        self.buf.write(CRLF)


def content_disposition_header(fn, disptype='file'):
    disposition = '%s; filename="%s"' % (
        disptype,
        quote(fn, safe='')
    )
    return {'Content-Disposition': disposition}


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
        subpart = part.open(headers=content_disposition_header(dirname))
        subpart.write_headers()
        
        files, subdirs = utils.ls_dir(dirname)

        for fn in files:
            if not fnmatch.fnmatch(fn, fnpattern):
                continue
            fullpath = os.path.join(dirname, fn)
            with open(fullpath, 'rb') as fp:
                subpart.add(fullpath,
                            fp.read(),
                            headers=content_disposition_header(fullpath))
            
        for subdir in subdirs:
            fullpath = os.path.join(dirname, subdir)
            walk(fullpath, subpart)
        
        subpart.close()
        return
    
    envelope = MultipartWriter(buf,
            headers=content_disposition_header(dirname, 'form-data'),
            subtype='form-data')
    
    walk(dirname, envelope)
    
    envelope.close()
    
    return buf.getvalue(), envelope.headers
