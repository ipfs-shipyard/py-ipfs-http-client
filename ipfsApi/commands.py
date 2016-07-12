"""Defines the skeleton of different command structures.

Classes:
Command -- A simple command that can make requests to a path.
ArgCommand -- A Command subclass for commands with arguments.
FileCommand -- A Command subclass for file-manipulation commands.
DownloadCommand -- A Command subclass for file download commands.
"""

from __future__ import absolute_import

import os

import six

from . import multipart
from .exceptions import InvalidArguments
from .multipart import default_chunk_size


class Command(object):
    """Defines a command.

    Public methods:
    __init__ -- creates a Command that will make requests to a given path
    request -- make a request to this command's path

    Instance variables:
    path -- the url path that this Command will make requests to
    """

    def __init__(self, path):
        """Creates a Command.

        Keyword arguments:
        path -- the url path that this Command makes requests to
        """
        self.path = path

    def request(self, client, *args, **kwargs):
        """Makes a request to the client with arguments.

        Keyword arguments:
        client -- the HTTP client to use for the request
        args -- unused unnamed arguments
        kwargs -- additional arguments to HTTP client's request
        """
        return client.request(self.path, **kwargs)


class ArgCommand(Command):
    """Defines a command that takes arguments.

    Subclass of Command.

    Public methods:
    __init__ -- extends Command constructor to also take a number of required
                arguments
    request -- makes a request to the ArgCommand's path with given arguments

    Instance variables:
    path -- the url path of that this command will send data to
    argc -- the number of arguments required by this command
    """

    def __init__(self, path, argc=None):
        """Creates an ArgCommand.

        Keyword arguments:
        path -- the url path to which the command with send data
        argc -- the number of arguments required by this command
        """
        Command.__init__(self, path)
        self.argc = argc

    def request(self, client, *args, **kwargs):
        """Makes a request to the client with arguments.

        Can raise an InvalidArgument if the wrong number of arguments is
        provided.

        Keyword arguments:
        client -- the HTTP client to use for the request
        args -- the arguments to the HTTP client's request
        kwargs -- additional arguments to HTTP client's request
        """
        if self.argc and len(args) != self.argc:
            raise InvalidArguments("[%s] command requires %d arguments." % (
                self.path, self.argc))
        return client.request(self.path, args=args, **kwargs)


class FileCommand(Command):
    """Defines a command for manipulating files.

    Subclass of Command.

    Public methods:
    request -- overrides Command's request to access a file or files
    files -- adds file-like objects as a multipart request to IPFS
    directory -- loads a directory recursively into IPFS

    Instance variables:
    path -- the path to make the file requests to
    """

    def request(self, client, args, f, **kwargs):
        """Makes a request for a file or files.

        Can only take one directory at a time, which will be
        traversed (optionally recursive).

        Keyword arguments:
        client -- the http client to send requests to
        args -- the arguments to the HTTP client's request
        f -- a file object, a filename, an iterable of filenames, an
                iterable of file objects, or a heterogeneous iterable of file
                objects and filenames
        kwargs -- additional arguments (include 'recursive' if recursively
                copying a directory)
        """
        if kwargs.pop('recursive', False):
            return self.directory(client, args, f, recursive=True, **kwargs)
        if isinstance(f, six.string_types) and os.path.isdir(f):
            return self.directory(client, args, f, **kwargs)
        else:
            return self.files(client, args, f, **kwargs)

    def files(self, client, args, files,
              chunk_size=default_chunk_size, **kwargs):
        """Adds file-like objects as a multipart request to IPFS.

        Keyword arguments:
        client -- the http client to send requests to
        args -- the arguments to the HTTP client's request
        files -- the files being requested
        chunk_size -- the size of the chunks to break the files into
        kwargs -- additional arguments to HTTP client's request
        """
        body, headers = multipart.stream_files(files,
                                               chunk_size=chunk_size)
        return client.request(self.path, args=args, data=body,
                              headers=headers, **kwargs)

    def directory(self, client, args, dirname,
                  match='*', recursive=False,
                  chunk_size=default_chunk_size, **kwargs):
        """Loads a directory recursively into IPFS.

        Files are matched against the given pattern.

        Keyword arguments:
        client -- the http client to send requests to
        args -- the arguments to the HTTP client's request
        dirname -- the name of the directory being requested
        match -- a pattern to match the files against
        recursive -- boolean for whether to load contents recursively
        chunk_size -- the size of the chunks to break the files into
        kwargs -- additional arguments to HTTP client's request
        """
        body, headers = multipart.stream_directory(dirname,
                                                   fnpattern=match,
                                                   recursive=recursive,
                                                   chunk_size=chunk_size)
        return client.request(self.path, args=args, data=body,
                              headers=headers, **kwargs)


class DownloadCommand(Command):
    """Downloads requested files.

    Subclass of Command

    Public methods:
    request -- make a request to this DownloadCommand's path to download a
                given file

    Instance variables:
    path -- the url path to send requests to
    """

    def request(self, client, *args, **kwargs):
        """Requests a download from the HTTP Client.

        See the HTTP client's doc for details of what to pass in.

        Keyword arguments:
        client -- the http client to send requests to
        args -- the arguments to the HTTP client
        kwargs -- additional arguments to the HTTP client
        """
        return client.download(self.path, args=args, **kwargs)
