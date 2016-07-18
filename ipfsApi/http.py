"""HTTP client for api requests.

This is pluggable into the IPFS Api client and
can/will eventually be supplemented with an asynchronous version.

Classes:
Client -- A TCP client for interacting with an IPFS daemon
"""
from __future__ import absolute_import

import contextlib
import re
import tarfile

import requests

from . import encoding
from .exceptions import ipfsApiError


def pass_defaults(func):
    """Decorator that returns a function named wrapper.

    When invoked, wrapper invokes func with default kwargs appended.

    Keyword arguments:
    func -- the function to append the default kwargs to
    """
    def wrapper(self, *args, **kwargs):
        merged = {}
        merged.update(self.defaults)
        merged.update(kwargs)
        return func(self, *args, **merged)
    return wrapper


class HTTPClient(object):
    """An HTTP client for interacting with the IPFS daemon.

    Public methods:
    __init__ -- initializes an instance of HTTPClient
    request -- makes an HTTP request to the IPFS daemon
    download -- makes a request to the IPFS daemon to download a file
    session -- a context manager for this client's session

    Instance variables:
    host -- the host the IPFS daemon is running on
    port -- the port the IPFS daemon is running on
    base -- the path at which the api calls are to be sent
    default_enc -- the default encoding of the HTTP client's response
    defaults -- the default options to be handled by pass_defaults
    """

    def __init__(self, host, port, base, default_enc, **defaults):
        """Initializes an instance of HTTPClient.

        Keyword arguments:
        host -- the host the IPFS daemon is running on
        port -- the port the IPFS daemon is running on
        base -- the path at which the api calls are to be sent
        default_enc -- the default encoding of the HTTP client's response
        defaults -- the default options to be handled by pass_defaults
        """
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
        """Makes an HTTP request to the IPFS daemon.

        This function returns the contents of the HTTP response from the IPFS
        daemon.

        Keyword Arguments:
        path -- the url path of this request
        args -- a list of parameters to be sent with the HTTP request
        files -- a file object, a filename, an iterable of filenames, an
                    iterable of file objects, or a heterogeneous iterable of
                    file objects and filenames
        opts -- a dictonary of parameters to be sent with the HTTP request
        decoder -- the encoding of the HTTP response, defaults to None
        kwargs -- additional arguments, used to determine HTTP request method
        """
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
        """Makes a request to the IPFS daemon to download a file.

        Downloads a file or files from IPFS into the current working
        directory, or the directory given by :filepath:.

        Keyword Arguments:
        path -- the url path of this request
        filepath -- the local path to where IPFS will download the files,
                    current working directory if None, defaults to None
        args -- a list of parameters to be sent with the HTTP request
        opts -- a dictonary of parameters to be sent with the HTTP request
        compress -- a flag that when true indicates that the response file
                    should be downloaded as a tar, defaults to True
        kwargs -- additional arguments
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
        """A context manager for this client's session.

        This function closes the current session when this client goes out of
        scope.
        """
        self._session = requests.session()
        yield
        self._session.close()
        self._session = None
