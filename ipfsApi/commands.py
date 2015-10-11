from __future__ import absolute_import

import os

import six

from . import multipart
from .exceptions import InvalidArguments
from .multipart import default_chunk_size


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

    def request(self, client, f, **kwargs):
        """
        Takes either a file object, a filename, an iterable of filenames, an
        iterable of file objects, or a heterogeneous iterable of file objects
        and filenames.  Can only take one directory at a time, which will be
        traversed (optionally recursive).
        """
        if kwargs.pop('recursive', False):
            return self.directory(client, f, recursive=True, **kwargs)
        if isinstance(f, six.string_types) and os.path.isdir(f):
            return self.directory(client, f, **kwargs)
        else:
            return self.files(client, f, **kwargs)

    def files(self, client, files, chunk_size=default_chunk_size, **kwargs):
        """
        Adds file-like objects as a multipart request to IPFS.
        """
        body, headers = multipart.stream_files(files,
                                               chunk_size=chunk_size)
        return client.request(self.path, data=body, headers=headers, **kwargs)

    def directory(self, client, dirname,
                  match='*', recursive=False,
                  chunk_size=default_chunk_size, **kwargs):
        """
        Loads a directory recursively into IPFS, files are matched against the
        given pattern.
        """
        body, headers = multipart.stream_directory(dirname,
                                                   fnpattern=match,
                                                   recursive=recursive,
                                                   chunk_size=chunk_size)
        return client.request(self.path, data=body, headers=headers, **kwargs)


class DownloadCommand(Command):

    def request(self, client, *args, **kwargs):
        return client.download(self.path, args=args, **kwargs)
