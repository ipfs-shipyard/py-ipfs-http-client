from __future__ import absolute_import

import os

from . import multipart
from .multipart import default_chunk_size
from .exceptions import InvalidArguments, FileCommandException

import six


class Command(object):

    def __init__(self, path):
        self.path = path

    def request(self, client, *args, **kwargs):
        return client.request(self.path, **kwargs)


class ArgCommand(Command):

    def __init__(self, path, argc=None):
        Command.__init__(self, path)
        self.argc = argc

    def request(self, client, *args, **kwargs):
        if self.argc and len(args) != self.argc:
            raise InvalidArguments("[%s] command requires %d arguments." % (
                self.path, self.argc))
        return client.request(self.path, args=args, **kwargs)


class FileCommand(Command):

    def __init__(self, path, accept_multiple=True):
        Command.__init__(self, path)
        self.accept_multiple = accept_multiple

    def request(self, client, f, **kwargs):
        """
        Takes either a file object, a filename, an iterable of filenames, an
        iterable of file objects, or a heterogeneous iterable of file objects
        and filenames.  Can only take one directory at a time, which will be
        traversed (optionally recursive).
        """
        if kwargs.pop('recursive', False):
            return self.directory(client, f, recursive=True, **kwargs)
        if isinstance(f, (list, tuple)):
            return self.multiple(client, f, **kwargs)
        if isinstance(f, six.string_types) and os.path.isdir(f):
            return self.directory(client, f, **kwargs)
        else:
            return self.single(client, f, **kwargs)

    def single(self, client, _file, chunk_size=default_chunk_size, **kwargs):
        """
        Adds a single file-like object to IPFS.
        """
        body, headers = multipart.stream_file(_file,
                                              chunk_size=chunk_size)
        return client.request(self.path, data=body, headers=headers, **kwargs)

    def multiple(self, client, files, chunk_size=default_chunk_size, **kwargs):
        """
        Adds multiple file-like objects as a multipart request to IPFS.
        """
        if not self.accept_multiple:
            raise FileCommandException(
                "[%s] does not accept multiple files." % self.path)
        body, headers = multipart.stream_files(files,
                                               chunk_size=chunk_size)
        return client.request(self.path, data=body, headers=headers, **kwargs)

    def directory(self, client, dirname,
                  fnpattern='*', recursive=False,
                  chunk_size=default_chunk_size, **kwargs):
        """
        Loads a directory recursively into IPFS, files are matched against the
        given pattern.
        """
        if not self.accept_multiple:
            raise FileCommandException(
                "[%s] does not accept multiple files." % self.path)
        body, headers = multipart.stream_directory(dirname,
                                                   fnpattern=fnpattern,
                                                   recursive=recursive,
                                                   chunk_size=chunk_size)
        return client.request(self.path, data=body, headers=headers, **kwargs)


class DownloadCommand(Command):

    def request(self, client, *args, **kwargs):
        return client.download(self.path, args=args, **kwargs)
