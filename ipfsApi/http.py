"""
HTTP client for api requests.  This is pluggable into the IPFS Api client and
can/will eventually be supplemented with an asynchronous version.
"""
from __future__ import absolute_import

import contextlib
import re
import tarfile

import requests

from . import encoding
from .exceptions import ipfsApiError


def pass_defaults(f):
    """
    Use instance default kwargs updated with those passed to function.
    """
    def wrapper(self, *args, **kwargs):
        merged = {}
        merged.update(self.defaults)
        merged.update(kwargs)
        return f(self, *args, **merged)
    return wrapper


class HTTPClient(object):

    def __init__(self, host, port, base, default_enc, **defaults):
        self.host = host
        self.port = port
        if not re.match('^https?://', host.lower()):
            host = 'http://' + host

        self.base = '%s:%s/%s' % (host, port, base)

        # default request keyword-args
        if 'opts' in defaults:
            defaults['opts'].update({'encoding': default_enc})
        else:
            defaults.update({'opts': {'encoding': default_enc}})

        self.default_enc  = encoding.get_encoding(default_enc)
        self.defaults = defaults
        self._session = None

    @pass_defaults
    def request(self, path,
                args=[], files=[], opts={},
                decoder=None, **kwargs):

        url = self.base + path

        params = []
        params.append(('stream-channels', 'true'))

        for opt in opts.items():
            params.append(opt)
        for arg in args:
            params.append(('arg', arg))

        method = 'post' if (files or 'data' in kwargs) else 'get'

        if self._session:
            res = self._session.request(method, url,
                                        params=params, files=files, **kwargs)
        else:
            res = requests.request(method, url,
                                   params=params, files=files, **kwargs)

        if not decoder:
            # return raw stream
            if kwargs.get('stream'):
                return res.raw

            if path == '/cat':
                # since <api>/cat only returns the raw data and not an encoded
                # object, dont't try to parse it automatically.
                ret = res.text
            else:
                try:
                    ret = self.default_enc.parse(res.text)
                except:
                    ret = res.text
        else:
            enc = encoding.get_encoding(decoder)
            try:
                ret = enc.parse(res.text)
            except:
                ret = res.text

        try:
            res.raise_for_status()
        except requests.exceptions.HTTPError:
            # If we have decoded an error response from the server,
            # use that as the exception message; otherwise, just pass
            # the exception on to the caller.
            if 'Message' in ret:
                raise ipfsApiError(ret['Message'])
            else:
                raise
        return ret

    @pass_defaults
    def download(self, path, filepath=None,
                 args=[], opts={},
                 compress=True, **kwargs):
        """
        Downloads a file or files from IPFS into the current working
        directory, or the directory given by :filepath:.
        """
        url = self.base + path
        wd = filepath or '.'

        params = []
        params.append(('stream-channels', 'true'))
        params.append(('archive', 'true'))
        if compress:
            params.append(('compress', 'true'))

        for opt in opts.items():
            params.append(opt)
        for arg in args:
            params.append(('arg', arg))

        method = 'get'

        if self._session:
            res = self._session.request(method, url,
                                        params=params, stream=True, **kwargs)
        else:
            res = requests.request(method, url,
                                   params=params, stream=True, **kwargs)

        res.raise_for_status()

        # try to stream download as a tar file stream
        mode = 'r|gz' if compress else 'r|'

        with tarfile.open(fileobj=res.raw, mode=mode) as tf:
            tf.extractall(path=wd)

    @contextlib.contextmanager
    def session(self):
        self._session = requests.session()
        yield
        self._session.close()
        self._session = None
