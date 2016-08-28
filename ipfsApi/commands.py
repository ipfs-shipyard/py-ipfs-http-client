"""Defines the skeleton of different command structures.
"""

from __future__ import absolute_import

import os

import six

from . import multipart
from .exceptions import InvalidArguments
from .multipart import default_chunk_size


class Command(object):
    """Defines a command.

    Parameters
    ----------
    path : str
        The URL that to use when making requests to the daemon
    """

    def __init__(self, path):
        self.path = path

    def request(self, client, *args, **kwargs):
        """Makes a request to the client with arguments.

        Parameters
        ----------
        client : ipfsApi.http.HTTPClient
            The HTTP client to use for the request
        args : list
            Unused unnamed arguments
        kwargs : dict
            Additional arguments for the HTTP client's request
        """
        return client.request(self.path, **kwargs)


class ArgCommand(Command):
    """Defines a command that takes arguments.

    Parameters
    ----------
    path : str
        The URL that to use when making requests to the daemon
    argc : int
        The number of arguments required by this command
    """

    def __init__(self, path, argc=None):
        Command.__init__(self, path)
        self.argc = argc

    def request(self, client, *args, **kwargs):
        """Makes a request to the client with arguments.

        Raises
        ------
        :class:`~ipfsApi.exceptions.InvalidArguments`
            The wrong number of positional arguments was provided.

        Parameters
        ----------
        client : ipfsApi.http.HTTPClient
            The HTTP client to use for the request
        args : list
            Positional arguments for the HTTP client's request
        kwargs : dict
            Additional arguments for the HTTP client's request
        """
        if self.argc and len(args) != self.argc:
            raise InvalidArguments(self.path, self.argc)
        return client.request(self.path, args=args, **kwargs)


class FileCommand(Command):
    """Defines a command for manipulating files.

    Parameters
    ----------
    path : str
        The URL that to use when making requests to the daemon
    """

    def request(self, client, args, f, **kwargs):
        """Makes a request for a file or files.

        Can only take one directory at a time, which will be traversed
        (optionally recursive).

        Parameters
        ----------
        client : ~ipfsApi.http.HTTPClient
            The HTTP client to use for the request
        args : list
            Positional arguments for the HTTP client's request
        f : :class:`io.RawIOBase` | :obj:`str` | :obj:`list`
            The file object(s) or path(s) to stream to the daemon
        recursive : bool
            Recursively copy a directory
        kwargs : dict
            Additional arguments for the HTTP client's request
        """
        if kwargs.pop('recursive', False):
            return self.directory(client, args, f, recursive=True, **kwargs)
        if isinstance(f, six.string_types) and os.path.isdir(f):
            return self.directory(client, args, f, **kwargs)
        else:
            return self.files(client, args, f, **kwargs)

    def files(self, client, args, files,
              chunk_size=default_chunk_size, **kwargs):
        """Copy single file-like objects into IPFS using a multipart request.

        Parameters
        ----------
        client : ~ipfsApi.http.HTTPClient
            The HTTP client to use for the request
        args : list
            Positional arguments for the HTTP client's request
        files : :class:`io.RawIOBase` | :obj:`str` | :obj:`list`
            The file object(s) or path(s) to stream to the daemon
        chunk_size : int
            The size of the chunks to break the file contents into
        kwargs : dict
            Additional arguments for the HTTP client's request
        """
        body, headers = multipart.stream_files(files,
                                               chunk_size=chunk_size)
        return client.request(self.path, args=args, data=body,
                              headers=headers, **kwargs)

    def directory(self, client, args, dirname,
                  match='*', recursive=False,
                  chunk_size=default_chunk_size, **kwargs):
        """Copy a directory recursively into IPFS using a multipart request.

        Files are matched against the given pattern.

        Parameters
        ----------
        client : ~ipfsApi.http.HTTPClient
            The HTTP client to use for the request
        args : list
            Positional arguments for the HTTP client's request
        dirname : str
            The filepath of the directory to stream
        match : str
            A pattern to match filepaths within the directory against
        recursive : bool
            Recursively copy a directory
        chunk_size : int
            The size of the chunks to break the file contents into
        kwargs : dict
            Additional arguments for the HTTP client's request
        """
        body, headers = multipart.stream_directory(dirname,
                                                   fnpattern=match,
                                                   recursive=recursive,
                                                   chunk_size=chunk_size)
        return client.request(self.path, args=args, data=body,
                              headers=headers, **kwargs)


class DownloadCommand(Command):
    """Downloads requested files.

    Parameters
    ----------
    path : str
        The URL that to use when making requests to the daemon
    """

    def request(self, client, *args, **kwargs):
        """Requests a download from the IPFS daemon using the HTTP Client.

        See the HTTP client's documentation for details of what to pass in.

        Parameters
        ----------
        client : ipfsApi.http.HTTPClient
            The HTTP client to use for the request
        args : list
            Positional arguments for the HTTP client's request
        kwargs : dict
            Additional arguments for the HTTP client's request
        """
        return client.download(self.path, args=args, **kwargs)
