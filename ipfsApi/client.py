# -*- coding: utf-8 -*-
"""IPFS API Bindings for Python.

Classes:

 * Client – a TCP client for interacting with an IPFS daemon
"""
from __future__ import absolute_import

from . import http, multipart, utils, exceptions, encoding
from .commands import ArgCommand, Command, DownloadCommand, FileCommand

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 5001
DEFAULT_BASE = 'api/v0'


class Client(object):
    """A TCP client for interacting with an IPFS daemon.

    Parameters
    ----------
    host : str
        Hostname or IP address of the computer running the ``ipfs daemon``
        node (defaults to the local system)
    port : int
        The API port of the IPFS deamon (usually 5001)
    base : str
        Path of the deamon's API (currently always ``api/v0``)
    default_enc : str
    """

    _clientfactory = http.HTTPClient

    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT,
                 base=DEFAULT_BASE, default_enc='json', **defaults):
        """Connects to the API port of an IPFS node."""

        self._client = self._clientfactory(host, port, base,
                                           default_enc, **defaults)

        # BASIC COMMANDS
        self._add                = FileCommand('/add')
        self._get                = DownloadCommand('/get')
        self._cat                = ArgCommand('/cat')
        self._ls                 = ArgCommand('/ls')
        self._refs               = ArgCommand('/refs')
        self._refs_local         = Command('/refs/local')

        # DATA STRUCTURE COMMANDS
        self._block_stat         = ArgCommand('/block/stat')
        self._block_get          = ArgCommand('/block/get')
        self._block_put          = FileCommand('/block/put')
        self._object_new         = ArgCommand('/object/new')
        self._bitswap_wantlist   = ArgCommand('/bitswap/wantlist')
        self._bitswap_stat       = Command('/bitswap/stat')
        self._bitswap_unwant     = ArgCommand('/bitswap/unwant')

        self._object_data        = ArgCommand('/object/data')
        self._object_links       = ArgCommand('/object/links')
        self._object_get         = ArgCommand('/object/get')
        self._object_put         = FileCommand('/object/put')
        self._object_stat        = ArgCommand('/object/stat')
        self._object_patch_append_data = FileCommand(
            '/object/patch/append-data')
        self._object_patch_add_link    = ArgCommand('/object/patch/add-link')
        self._object_patch_rm_link     = ArgCommand('/object/patch/rm-link')
        self._object_patch_set_data    = FileCommand('/object/patch/set-data')
        self._file_ls            = ArgCommand('/file/ls')

        # ADVANCED COMMANDS
        self._resolve            = ArgCommand('/resolve')
        self._name_publish       = ArgCommand('/name/publish')
        self._name_resolve       = ArgCommand('/name/resolve')
        self._dns                = ArgCommand('/dns')
        self._pin_add            = ArgCommand('/pin/add')
        self._pin_rm             = ArgCommand('/pin/rm')
        self._pin_ls             = Command('/pin/ls')
        self._repo_gc            = Command('/repo/gc')
        self._repo_stat          = Command('/repo/stat')
        self._repo_fsck          = Command('/repo/stat')
        self._repo_version       = Command('/repo/version')
        self._repo_verify        = Command('/repo/verify')

        # NETWORK COMMANDS
        self._id                 = Command('/id')
        self._bootstrap          = Command('/bootstrap')
        self._bootstrap_add      = ArgCommand('/bootstrap/add')
        self._bootstrap_rm       = ArgCommand('/bootstrap/rm')
        self._swarm_peers        = Command('/swarm/peers')
        self._swarm_addrs        = Command('/swarm/addrs')
        self._swarm_connect      = ArgCommand('/swarm/connect')
        self._swarm_disconnect   = ArgCommand('/swarm/disconnect')
        self._swarm_filters_add  = ArgCommand('/swarm/filters/add')
        self._swarm_filters_rm   = ArgCommand('/swarm/filters/rm')
        self._dht_query          = ArgCommand('/dht/query')
        self._dht_findprovs      = ArgCommand('/dht/findprovs')
        self._dht_findpeer       = ArgCommand('/dht/findpeer')
        self._dht_get            = ArgCommand('/dht/get')
        self._dht_put            = ArgCommand('/dht/put', argc=2)
        self._ping               = ArgCommand('/ping')

        # TOOL COMMANDS
        self._config             = ArgCommand('/config')
        self._config_show        = Command('/config/show')
        self._config_replace     = ArgCommand('/config/replace')
        self._log_level          = ArgCommand('/log/level')
        self._log_ls             = Command('/log/ls')
        self._log_tail           = Command('/log/tail')
        self._version            = Command('/version')

        # MFS COMMANDS
        self._files_cp           = ArgCommand('/files/cp')
        self._files_ls           = ArgCommand('/files/ls')
        self._files_mkdir        = ArgCommand('/files/mkdir')
        self._files_stat         = ArgCommand('/files/stat')
        self._files_rm           = ArgCommand('/files/rm')
        self._files_read         = ArgCommand('/files/read')
        self._files_write        = FileCommand('/files/write')
        self._files_mv           = ArgCommand('/files/mv')

    def add(self, files, recursive=False, **kwargs):
        """Add a file, or directory of files to IPFS.

        .. code-block:: python

            >>> with io.open('nurseryrhyme.txt', 'w', encoding='utf-8') as f:
            ...     numbytes = f.write('Mary had a little lamb')
            >>> c.add('nurseryrhyme.txt')
            {'Hash': 'QmZfF6C9j4VtoCsTp4KSrhYH47QMd3DNXVZBKaxJdhaPab',
             'Name': 'nurseryrhyme.txt'}

        Parameters
        ----------
        files : str
            A filepath to either a file or directory
        recursive : bool
            Controls if files in subdirectories are added or not

        Returns
        -------
            dict: File name and hash of the added file node
        """
        return self._add.request(self._client, (), files,
                                 recursive=recursive, **kwargs)

    def get(self, multihash, **kwargs):
        """Downloads a file, or directory of files from IPFS.

        Files are placed in the current working directory.

        Parameters
        ----------
        multihash : str
            The path to the IPFS object(s) to be outputted
        """
        return self._get.request(self._client, multihash, **kwargs)

    def cat(self, multihash, **kwargs):
        r"""Retrieves the contents of a file identified by hash.

        .. code-block:: python

            >>> c.cat('QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDxdXBFca7D')
            Traceback (most recent call last):
              ...
            ipfsApi.exceptions.Error: this dag node is a directory
            >>> c.cat('QmeKozNssnkJ4NcyRidYgDY2jfRZqVEoRGfipkgath71bX')
            b'<!DOCTYPE html>\n<html>\n\n<head>\n<title>ipfs example viewer</…'

        Parameters
        ----------
        multihash : str
            The path to the IPFS object(s) to be retrieved

        Returns
        -------
            str : File contents
        """
        return self._cat.request(self._client, multihash, **kwargs)

    def ls(self, multihash, **kwargs):
        """Returns a list of objects linked to by the given hash.

        .. code-block:: python

            >>> c.ls('QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDxdXBFca7D')
            {'Objects': [
              {'Hash': 'QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDxdXBFca7D',
               'Links': [
                {'Hash': 'Qmd2xkBfEwEs9oMTk77A6jrsgurpF3ugXSg7dtPNFkcNMV',
                 'Name': 'Makefile',          'Size': 174, 'Type': 2},
                 …
                {'Hash': 'QmSY8RfVntt3VdxWppv9w5hWgNrE31uctgTiYwKir8eXJY',
                 'Name': 'published-version', 'Size': 55,  'Type': 2}
                ]}
              ]}

        Parameters
        ----------
        multihash : str
            The path to the IPFS object(s) to list links from

        Returns
        -------
            dict : Directory information and contents
        """
        return self._ls.request(self._client, multihash, **kwargs)

    def refs(self, multihash, **kwargs):
        """Returns a list of hashes of objects referenced by the given hash.

        .. code-block:: python

            >>> c.refs('QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDxdXBFca7D')
            [{'Ref': 'Qmd2xkBfEwEs9oMTk77A6jrsgurpF3ugXSg7 … cNMV', 'Err': ''},
             …
             {'Ref': 'QmSY8RfVntt3VdxWppv9w5hWgNrE31uctgTi … eXJY', 'Err': ''}]

        Parameters
        ----------
        multihash : str
            Path to the object(s) to list refs from

        Returns
        -------
            list
        """
        return self._refs.request(self._client, multihash, **kwargs)

    def refs_local(self, **kwargs):
        """Displays the hashes of all local objects.

        .. code-block:: python

            >>> c.refs_local()
            [{'Ref': 'Qmd2xkBfEwEs9oMTk77A6jrsgurpF3ugXSg7 … cNMV', 'Err': ''},
             …
             {'Ref': 'QmSY8RfVntt3VdxWppv9w5hWgNrE31uctgTi … eXJY', 'Err': ''}]

        Returns
        -------
            list
        """
        return self._refs_local.request(self._client, **kwargs)

    def block_stat(self, multihash, **kwargs):
        """Returns a dict with the size of the block with the given hash.

        .. code-block:: python

            >>> c.block_stat('QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDxdXBFca7D')
            {'Key':  'QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDxdXBFca7D',
             'Size': 258}

        Parameters
        ----------
        multihash : str
            The base58 multihash of an existing block to stat

        Returns
        -------
            dict : Information about the requested block
        """
        return self._block_stat.request(self._client, multihash, **kwargs)

    def block_get(self, multihash, **kwargs):
        r"""Returns the raw contents of a block.

        .. code-block:: python

            >>> c.block_get('QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDxdXBFca7D')
            b'\x121\n"\x12 \xdaW>\x14\xe5\xc1\xf6\xe4\x92\xd1 … \n\x02\x08\x01'

        Parameters
        ----------
        multihash : str
            The base58 multihash of an existing block to get

        Returns
        -------
            str : Value of the requested block
        """
        return self._block_get.request(self._client, multihash, **kwargs)

    def block_put(self, file, **kwargs):
        """Stores the contents of the given file object as an IPFS block.

        .. code-block:: python

            >>> c.block_put(io.BytesIO(b'Mary had a little lamb'))
                {'Key':  'QmeV6C6XVt1wf7V7as7Yak3mxPma8jzpqyhtRtCvpKcfBb',
                 'Size': 22}

        Parameters
        ----------
        file : io.RawIOBase
            The data to be stored as an IPFS block

        Returns
        -------
            dict : Information about the new block

                   See :meth:`~ipfsApi.Client.block_stat`
        """
        return self._block_put.request(self._client, (), file, **kwargs)

    def bitswap_wantlist(self, peer=None, **kwargs):
        """Returns blocks currently on the bitswap wantlist.

        .. code-block:: python

            >>> c.bitswap_wantlist()
            {'Keys': [
                'QmeV6C6XVt1wf7V7as7Yak3mxPma8jzpqyhtRtCvpKcfBb',
                'QmdCWFLDXqgdWQY9kVubbEHBbkieKd3uo7MtCm7nTZZE9K',
                'QmVQ1XvYGF19X4eJqz1s7FJYJqAxFC4oqh3vWJJEXn66cp'
            ]}

        Parameters
        ----------
        peer : str
            Peer to show wantlist for.

        Returns
        -------
            dict : List of wanted blocks
        """
        return self._bitswap_wantlist.request(self._client, peer, **kwargs)

    def bitswap_stat(self, **kwargs):
        """Returns some diagnostic information from the bitswap agent.

        .. code-block:: python

            >>> c.bitswap_stat()
            {'BlocksReceived': 96,
             'DupBlksReceived': 73,
             'DupDataReceived': 2560601,
             'ProviderBufLen': 0,
             'Peers': [
                'QmNZFQRxt9RMNm2VVtuV2Qx7q69bcMWRVXmr5CEkJEgJJP',
                'QmNfCubGpwYZAQxX8LQDsYgB48C4GbfZHuYdexpX9mbNyT',
                'QmNfnZ8SCs3jAtNPc8kf3WJqJqSoX7wsX7VqkLdEYMao4u',
                …
             ],
             'Wantlist': [
                'QmeV6C6XVt1wf7V7as7Yak3mxPma8jzpqyhtRtCvpKcfBb',
                'QmdCWFLDXqgdWQY9kVubbEHBbkieKd3uo7MtCm7nTZZE9K',
                'QmVQ1XvYGF19X4eJqz1s7FJYJqAxFC4oqh3vWJJEXn66cp'
             ]
            }

        Returns
        -------
            dict : Statistics, peers and wanted blocks
        """
        return self._bitswap_stat.request(self._client, **kwargs)

    def bitswap_unwant(self, key, **kwargs):
        """
        Remove a given block from wantlist.

        Parameters
        ----------
        key : str
            Key to remove from wantlist.
        """
        return self._bitswap_unwant.request(self._client, key, **kwargs)

    def object_data(self, multihash, **kwargs):
        r"""Returns the raw bytes in an IPFS object.

        .. code-block:: python

            >>> c.object_data('QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDxdXBFca7D')
            b'\x08\x01'

        Parameters
        ----------
        multihash : str
            Key of the object to retrieve, in base58-encoded multihash format

        Returns
        -------
            str : Raw object data
        """
        return self._object_data.request(self._client, multihash, **kwargs)

    def object_new(self, template=None, **kwargs):
        """Creates a new object from an IPFS template.

        By default this creates and returns a new empty merkledag node, but you
        may pass an optional template argument to create a preformatted node.

        .. code-block:: python

            >>> c.object_new()
            {u'Hash': u'QmdfTbBqBPQ7VNxZEYEj14VmRuZBkqFbiwReogJgS1zR1n'}

        Parameters
        ----------
        template : str
            Blueprints from which to construct the new object. Possible values:

             * ``"unixfs-dir"``
             * ``None``

        Returns
        -------
            dict : Object hash
        """
        if template:
            return self._object_new.request(self._client, template, **kwargs)
        else:
            return self._object_new.request(self._client, **kwargs)

    def object_links(self, multihash, **kwargs):
        """Returns the links pointed to by the specified object.

        .. code-block:: python

            >>> c.object_links('QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDx … ca7D')
            {'Hash': 'QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDxdXBFca7D',
             'Links': [
                {'Hash': 'Qmd2xkBfEwEs9oMTk77A6jrsgurpF3ugXSg7dtPNFkcNMV',
                 'Name': 'Makefile',          'Size': 174},
                {'Hash': 'QmeKozNssnkJ4NcyRidYgDY2jfRZqVEoRGfipkgath71bX',
                 'Name': 'example',           'Size': 1474},
                {'Hash': 'QmZAL3oHMQYqsV61tGvoAVtQLs1WzRe1zkkamv9qxqnDuK',
                 'Name': 'home',              'Size': 3947},
                {'Hash': 'QmZNPyKVriMsZwJSNXeQtVQSNU4v4KEKGUQaMT61LPahso',
                 'Name': 'lib',               'Size': 268261},
                {'Hash': 'QmSY8RfVntt3VdxWppv9w5hWgNrE31uctgTiYwKir8eXJY',
                 'Name': 'published-version', 'Size': 55}]}

        Parameters
        ----------
        multihash : str
            Key of the object to retrieve, in base58-encoded multihash format

        Returns
        -------
            dict : Object hash and merkedag links
        """
        return self._object_links.request(self._client, multihash, **kwargs)

    def object_get(self, multihash, **kwargs):
        """Get and serialize the DAG node named by multihash.

        .. code-block:: python

            >>> c.object_get('QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDxdXBFca7D')
            {'Data': '\x08\x01',
             'Links': [
                {'Hash': 'Qmd2xkBfEwEs9oMTk77A6jrsgurpF3ugXSg7dtPNFkcNMV',
                 'Name': 'Makefile',          'Size': 174},
                {'Hash': 'QmeKozNssnkJ4NcyRidYgDY2jfRZqVEoRGfipkgath71bX',
                 'Name': 'example',           'Size': 1474},
                {'Hash': 'QmZAL3oHMQYqsV61tGvoAVtQLs1WzRe1zkkamv9qxqnDuK',
                 'Name': 'home',              'Size': 3947},
                {'Hash': 'QmZNPyKVriMsZwJSNXeQtVQSNU4v4KEKGUQaMT61LPahso',
                 'Name': 'lib',               'Size': 268261},
                {'Hash': 'QmSY8RfVntt3VdxWppv9w5hWgNrE31uctgTiYwKir8eXJY',
                 'Name': 'published-version', 'Size': 55}]}

        Parameters
        ----------
        multihash : str
            Key of the object to retrieve, in base58-encoded multihash format

        Returns
        -------
            dict : Object data and links
        """
        return self._object_get.request(self._client, multihash, **kwargs)

    def object_put(self, file, **kwargs):
        """Stores input as a DAG object and returns its key.

        .. code-block:: python

            >>> c.object_put(io.BytesIO(b'''
            ...       {
            ...           "Data": "another",
            ...           "Links": [ {
            ...               "Name": "some link",
            ...               "Hash": "QmXg9Pp2ytZ14xgmQjYEiHjVjMFXzCV … R39V",
            ...               "Size": 8
            ...           } ]
            ...       }'''))
            {'Hash': 'QmZZmY4KCu9r3e7M2Pcn46Fc5qbn6NpzaAGaYb22kbfTqm',
             'Links': [
                {'Hash': 'QmXg9Pp2ytZ14xgmQjYEiHjVjMFXzCVVEcRTWJBmLgR39V',
                 'Size': 8, 'Name': 'some link'}
             ]
            }

        Parameters
        ----------
        file : io.RawIOBase
            (JSON) object from which the DAG object will be created

        Returns
        -------
            dict : Hash and links of the created DAG object

                   See :meth:`~ipfsApi.Object.object_links`
        """
        return self._object_put.request(self._client, (), file, **kwargs)

    def object_stat(self, multihash, **kwargs):
        """Get stats for the DAG node named by multihash.

        .. code-block:: python

            >>> c.object_stat('QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDxdXBFca7D')
            {'LinksSize': 256, 'NumLinks': 5,
             'Hash': 'QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDxdXBFca7D',
             'BlockSize': 258, 'CumulativeSize': 274169, 'DataSize': 2}

        Parameters
        ----------
        multihash : str
            Key of the object to retrieve, in base58-encoded multihash format

        Returns
        -------
            dict
        """
        return self._object_stat.request(self._client, multihash, **kwargs)

    def object_patch_append_data(self, multihash, new_data, **kwargs):
        """Creates a new merkledag object based on an existing one.

        The new object will have the provided data appended to it,
        and will thus have a new Hash.

        .. code-block:: python

            >>> c.object_patch_append_data("QmZZmY … fTqm", io.BytesIO(b"bla"))
            {'Hash': 'QmR79zQQj2aDfnrNgczUhvf2qWapEfQ82YQRt3QjrbhSb2'}

        Parameters
        ----------
        multihash : str
            The hash of an ipfs object to modify
        new_data : io.RawIOBase
            The data to append to the object's data section

        Returns
        -------
            dict : Hash of new object
        """
        return self._object_patch_append_data.request(self._client,
                                                      [multihash],
                                                      new_data,
                                                      **kwargs)

    def object_patch_add_link(self, root, name, ref, create=False, **kwargs):
        """Creates a new merkledag object based on an existing one.

        The new object will have a link to the provided object.

        .. code-block:: python

            >>> c.object_patch_add_link(
            ...     'QmR79zQQj2aDfnrNgczUhvf2qWapEfQ82YQRt3QjrbhSb2',
            ...     'Johnny',
            ...     'QmR79zQQj2aDfnrNgczUhvf2qWapEfQ82YQRt3QjrbhSb2'
            ... )
            {'Hash': 'QmNtXbF3AjAk59gQKRgEdVabHcSsiPUnJwHnZKyj2x8Z3k'}

        Parameters
        ----------
        root : str
            IPFS hash for the object being modified
        name : str
            name for the new link
        ref : str
            IPFS hash for the object being linked to
        create : bool
            Create intermediary nodes

        Returns
        -------
            dict : Hash of new object
        """
        kwargs.setdefault("opts", {"create": create})
        return self._object_patch_add_link.request(self._client,
                                                   (root, name, ref),
                                                   **kwargs)

    def object_patch_rm_link(self, root, link, **kwargs):
        """Creates a new merkledag object based on an existing one.

        The new object will lack a link to the specified object.

        .. code-block:: python

            >>> c.object_patch_rm_link(
            ...     'QmNtXbF3AjAk59gQKRgEdVabHcSsiPUnJwHnZKyj2x8Z3k',
            ...     'Johnny'
            ... )
            {'Hash': 'QmR79zQQj2aDfnrNgczUhvf2qWapEfQ82YQRt3QjrbhSb2'}

        Parameters
        ----------
        root : str
            IPFS hash of the object to modify
        link : str
            name of the link to remove

        Returns
        -------
            dict : Hash of new object
        """
        return self._object_patch_rm_link.request(self._client,
                                                  (root, link),
                                                  **kwargs)

    def object_patch_set_data(self, root, data, **kwargs):
        """Creates a new merkledag object based on an existing one.

        The new object will have the same links as the old object but
        with the provided data instead of the old object's data contents.

        .. code-block:: python

            >>> c.object_patch_set_data(
            ...     'QmNtXbF3AjAk59gQKRgEdVabHcSsiPUnJwHnZKyj2x8Z3k',
            ...     io.BytesIO(b'bla')
            ... )
            {'Hash': 'QmSw3k2qkv4ZPsbu9DVEJaTMszAQWNgM1FTFYpfZeNQWrd'}

        Parameters
        ----------
        root : str
            IPFS hash of the object to modify
        data : io.RawIOBase
            The new data to store in root

        Returns
        -------
            dict : Hash of new object
        """
        return self._object_patch_set_data.request(self._client,
                                                   [root],
                                                   data,
                                                   **kwargs)

    def file_ls(self, multihash, **kwargs):
        """Lists directory contents for Unix filesystem objects.

        The result contains size information. For files, the child size is the
        total size of the file contents. For directories, the child size is the
        IPFS link size.

        The path can be a prefixless reference; in this case, it is assumed
        that it is an ``/ipfs/`` reference and not ``/ipns/``.

        .. code-block:: python

            >>> c.file_ls('QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDxdXBFca7D')
            {'Arguments': {'QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDxdXBFca7D':
                           'QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDxdXBFca7D'},
             'Objects': {
               'QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDxdXBFca7D': {
                 'Hash': 'QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDxdXBFca7D',
                 'Size': 0, 'Type': 'Directory',
                 'Links': [
                   {'Hash': 'Qmd2xkBfEwEs9oMTk77A6jrsgurpF3ugXSg7dtPNFkcNMV',
                    'Name': 'Makefile', 'Size': 163,    'Type': 'File'},
                   {'Hash': 'QmeKozNssnkJ4NcyRidYgDY2jfRZqVEoRGfipkgath71bX',
                    'Name': 'example',  'Size': 1463,   'Type': 'File'},
                   {'Hash': 'QmZAL3oHMQYqsV61tGvoAVtQLs1WzRe1zkkamv9qxqnDuK',
                    'Name': 'home',     'Size': 3947,   'Type': 'Directory'},
                   {'Hash': 'QmZNPyKVriMsZwJSNXeQtVQSNU4v4KEKGUQaMT61LPahso',
                    'Name': 'lib',      'Size': 268261, 'Type': 'Directory'},
                   {'Hash': 'QmSY8RfVntt3VdxWppv9w5hWgNrE31uctgTiYwKir8eXJY',
                    'Name': 'published-version',
                    'Size': 47, 'Type': 'File'}
                   ]
               }
            }}

        Parameters
        ----------
        multihash : str
            The path to the object(s) to list links from

        Returns
        -------
            dict
        """
        return self._file_ls.request(self._client, multihash, **kwargs)

    def resolve(self, name, recursive=False, **kwargs):
        """Accepts an identifier and resolves it to the referenced item.

        There are a number of mutable name protocols that can link among
        themselves and into IPNS. For example IPNS references can (currently)
        point at an IPFS object, and DNS links can point at other DNS links,
        IPNS entries, or IPFS objects. This command accepts any of these
        identifiers.

        .. code-block:: python

            >>> c.resolve("/ipfs/QmTkzDwWqPbnAh5YiV5VwcTLnGdw … ca7D/Makefile")
            {'Path': '/ipfs/Qmd2xkBfEwEs9oMTk77A6jrsgurpF3ugXSg7dtPNFkcNMV'}
            >>> c.resolve("/ipns/ipfs.io")
            {'Path': '/ipfs/QmTzQ1JRkWErjk39mryYw2WVaphAZNAREyMchXzYQ7c15n'}

        Parameters
        ----------
        name : str
            The name to resolve
        recursive : bool
            Resolve until the result is an IPFS name

        Returns
        -------
            dict : IPFS path of resource
        """
        kwargs.setdefault("opts", {"recursive": recursive})
        return self._resolve.request(self._client, name, **kwargs)

    def name_publish(self, ipfs_path, resolve=True, lifetime="24h", ttl=None,
                     **kwargs):
        """Publishes an object to IPNS.

        IPNS is a PKI namespace, where names are the hashes of public keys, and
        the private key enables publishing new (signed) values. In publish, the
        default value of *name* is your own identity public key.

        .. code-block:: python

            >>> c.name_publish('/ipfs/QmfZY61ukoQuCX8e5Pt7v8pRfhkyxwZK … GZ5d')
            {'Value': '/ipfs/QmfZY61ukoQuCX8e5Pt7v8pRfhkyxwZKZMTodAtmvyGZ5d',
             'Name': 'QmVgNoP89mzpgEAAqK8owYoDEyB97MkcGvoWZir8otE9Uc'}

        Parameters
        ----------
        ipfs_path : str
            IPFS path of the object to be published
        resolve : bool
            Resolve given path before publishing
        lifetime : str
            Time duration that the record will be valid for

            Accepts durations such as ``"300s"``, ``"1.5h"`` or ``"2h45m"``.
            Valid units are:

             * ``"ns"``
             * ``"us"`` (or ``"µs"``)
             * ``"ms"``
             * ``"s"``
             * ``"m"``
             * ``"h"``
        ttl : int
            Time duration this record should be cached for

        Returns
        -------
            dict : IPNS hash and the IPFS path it points at
        """
        opts = {"lifetime": lifetime, "resolve": resolve}
        if ttl:
            opts["ttl"] = ttl

        kwargs.setdefault("opts", opts)
        return self._name_publish.request(self._client, ipfs_path, **kwargs)

    def name_resolve(self, name=None, **kwargs):
        """Gets the value currently published at an IPNS name.

        IPNS is a PKI namespace, where names are the hashes of public keys, and
        the private key enables publishing new (signed) values. In resolve, the
        default value of ``name`` is your own identity public key.

        .. code-block:: python

            >>> c.name_resolve()
            {'Path': '/ipfs/QmfZY61ukoQuCX8e5Pt7v8pRfhkyxwZKZMTodAtmvyGZ5d'}

        Parameters
        ----------
        name : str
            The IPNS name to resolve (defaults to the connected node)

        Returns
        -------
            dict : The IPFS path the IPNS hash points at
        """
        args = [name] if name is not None else []
        return self._name_resolve.request(self._client, *args, **kwargs)

    def dns(self, domain_name, recursive=False, **kwargs):
        """Resolves DNS links to the referenced object.

        Multihashes are hard to remember, but domain names are usually easy to
        remember. To create memorable aliases for multihashes, DNS TXT records
        can point to other DNS links, IPFS objects, IPNS keys, etc.
        This command resolves those links to the referenced object.

        For example, with this DNS TXT record::

            >>> import dns.resolver
            >>> a = dns.resolver.query("ipfs.io", "TXT")
            >>> a.response.answer[0].items[0].to_text()
            '"dnslink=/ipfs/QmTzQ1JRkWErjk39mryYw2WVaphAZNAREyMchXzYQ7c15n"'

        The resolver will give::

            >>> c.dns("ipfs.io")
            {'Path': '/ipfs/QmTzQ1JRkWErjk39mryYw2WVaphAZNAREyMchXzYQ7c15n'}

        Parameters
        ----------
        domain_name : str
           The domain-name name to resolve
        recursive : bool
            Resolve until the name is not a DNS link

        Returns
        -------
            dict : Resource were a DNS entry points to
        """
        kwargs.setdefault("opts", {"recursive": recursive})
        return self._dns.request(self._client, domain_name, **kwargs)

    def pin_add(self, path, *paths, **kwargs):
        """Pins objects to local storage.

        Stores an IPFS object(s) from a given path locally to disk.

        .. code-block:: python

            >>> c.pin_add("QmfZY61ukoQuCX8e5Pt7v8pRfhkyxwZKZMTodAtmvyGZ5d")
            {'Pins': ['QmfZY61ukoQuCX8e5Pt7v8pRfhkyxwZKZMTodAtmvyGZ5d']}

        Parameters
        ----------
        path : str
            Path to object(s) to be pinned
        recursive : bool
            Recursively unpin the object linked to by the specified object(s)

        Returns
        -------
            dict : List of IPFS objects that have been pinned
        """
        # Python 2 does not support kw-only parameters after glob parameters
        if "recursive" in kwargs:
            kwargs.setdefault("opts", {"recursive": kwargs["recursive"]})
            del kwargs["recursive"]

        return self._pin_add.request(self._client, path, *paths, **kwargs)

    def pin_rm(self, path, *paths, **kwargs):
        """Removes a pinned object from local storage.

        Removes the pin from the given object allowing it to be garbage
        collected if needed.

        .. code-block:: python

            >>> c.pin_rm('QmfZY61ukoQuCX8e5Pt7v8pRfhkyxwZKZMTodAtmvyGZ5d')
            {'Pins': ['QmfZY61ukoQuCX8e5Pt7v8pRfhkyxwZKZMTodAtmvyGZ5d']}

        Parameters
        ----------
        path : str
            Path to object(s) to be unpinned
        recursive : bool
            Recursively unpin the object linked to by the specified object(s)

        Returns
        -------
            dict : List of IPFS objects that have been unpinned
        """
        # Python 2 does not support kw-only parameters after glob parameters
        if "recursive" in kwargs:
            kwargs.setdefault("opts", {"recursive": kwargs["recursive"]})
            del kwargs["recursive"]

        return self._pin_rm.request(self._client, path, *paths, **kwargs)

    def pin_ls(self, type="all", **kwargs):
        """Lists objects pinned to local storage.

        By default, all pinned objects are returned, but the ``type`` flag or
        arguments can restrict that to a specific pin type or to some specific
        objects respectively.

        .. code-block:: python

            >>> c.pin_ls()
            {'Keys': {
                'QmNNPMA1eGUbKxeph6yqV8ZmRkdVat … YMuz': {'Type': 'recursive'},
                'QmNPZUCeSN5458Uwny8mXSWubjjr6J … kP5e': {'Type': 'recursive'},
                'QmNg5zWpRMxzRAVg7FTQ3tUxVbKj8E … gHPz': {'Type': 'indirect'},
                …
                'QmNiuVapnYCrLjxyweHeuk6Xdqfvts … wCCe': {'Type': 'indirect'}}}

        Parameters
        ----------
        type : "str"
            The type of pinned keys to list. Can be:

             * ``"direct"``
             * ``"indirect"``
             * ``"recursive"``
             * ``"all"``

        Returns
        -------
            dict : Hashes of pinned IPFS objects and why they are pinned
        """
        kwargs.setdefault("opts", {"type": type})
        return self._pin_ls.request(self._client, **kwargs)

    def repo_gc(self, **kwargs):
        """Removes stored objects that are not pinned from the repo.

        .. code-block:: python

            >>> c.repo_gc()
            [{'Key': 'QmNPXDC6wTXVmZ9Uoc8X1oqxRRJr4f1sDuyQuwaHG2mpW2'},
             {'Key': 'QmNtXbF3AjAk59gQKRgEdVabHcSsiPUnJwHnZKyj2x8Z3k'},
             {'Key': 'QmRVBnxUCsD57ic5FksKYadtyUbMsyo9KYQKKELajqAp4q'},
             …
             {'Key': 'QmYp4TeCurXrhsxnzt5wqLqqUz8ZRg5zsc7GuUrUSDtwzP'}]

        Performs a garbage collection sweep of the local set of
        stored objects and remove ones that are not pinned in order
        to reclaim hard disk space. Returns the hashes of all collected
        objects.

        Returns
        -------
            dict : List of IPFS objects that have been removed
        """
        return self._repo_gc.request(self._client, **kwargs)

    def repo_stat(self, **kwargs):
        """Displays the repo's status.

        Returns the number of objects in the repo and the repo's size,
        version, and path.

        .. code-block:: python

            >>> c.repo_stat()
            {'NumObjects': 354,
             'RepoPath': '…/.local/share/ipfs',
             'Version': 'fs-repo@4',
             'RepoSize': 13789310}

        Returns
        -------
            dict : General information about the IPFS file repository

        +------------+-------------------------------------------------+
        | NumObjects | Number of objects in the local repo.            |
        +------------+-------------------------------------------------+
        | RepoPath   | The path to the repo being currently used.      |
        +------------+-------------------------------------------------+
        | RepoSize   | Size in bytes that the repo is currently using. |
        +------------+-------------------------------------------------+
        | Version    | The repo version.                               |
        +------------+-------------------------------------------------+
        """
        return self._repo_stat.request(self._client, **kwargs)

    def id(self, peer=None, **kwargs):
        """Shows IPFS Node ID info.

        Returns the PublicKey, ProtocolVersion, ID, AgentVersion and
        Addresses of the connected daemon or some other node.

        .. code-block:: python

            >>> c.id()
            {'ID': 'QmVgNoP89mzpgEAAqK8owYoDEyB97MkcGvoWZir8otE9Uc',
            'PublicKey': 'CAASpgIwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggE … BAAE=',
            'AgentVersion': 'go-libp2p/3.3.4',
            'ProtocolVersion': 'ipfs/0.1.0',
            'Addresses': [
                '/ip4/127.0.0.1/tcp/4001/ipfs/QmVgNoP89mzpgEAAqK8owYo … E9Uc',
                '/ip4/10.1.0.172/tcp/4001/ipfs/QmVgNoP89mzpgEAAqK8owY … E9Uc',
                '/ip4/172.18.0.1/tcp/4001/ipfs/QmVgNoP89mzpgEAAqK8owY … E9Uc',
                '/ip6/::1/tcp/4001/ipfs/QmVgNoP89mzpgEAAqK8owYoDEyB97 … E9Uc',
                '/ip6/fccc:7904:b05b:a579:957b:deef:f066:cad9/tcp/400 … E9Uc',
                '/ip6/fd56:1966:efd8::212/tcp/4001/ipfs/QmVgNoP89mzpg … E9Uc',
                '/ip6/fd56:1966:efd8:0:def1:34d0:773:48f/tcp/4001/ipf … E9Uc',
                '/ip6/2001:db8:1::1/tcp/4001/ipfs/QmVgNoP89mzpgEAAqK8 … E9Uc',
                '/ip4/77.116.233.54/tcp/4001/ipfs/QmVgNoP89mzpgEAAqK8 … E9Uc',
                '/ip4/77.116.233.54/tcp/10842/ipfs/QmVgNoP89mzpgEAAqK … E9Uc']}

        Parameters
        ----------
        peer : str
            Peer.ID of the node to look up (local node if ``None``)

        Returns
        -------
            dict : Information about the IPFS node
        """
        peers = [peer] if peer is not None else []
        return self._id.request(self._client, *peers, **kwargs)

    def bootstrap(self, **kwargs):
        """Compatiblity alias for :meth:`~ipfsApi.Client.bootstrap_list`."""
        self.bootstrap_list(**kwargs)

    def bootstrap_list(self, **kwargs):
        """Returns the addresses of peers used during initial discovery of the
        IPFS network.

        Peers are output in the format ``<multiaddr>/<peerID>``.

        .. code-block:: python

            >>> c.bootstrap_list()
            {'Peers': [
                '/ip4/104.131.131.82/tcp/4001/ipfs/QmaCpDMGvV2BGHeYER … uvuJ',
                '/ip4/104.236.176.52/tcp/4001/ipfs/QmSoLnSGccFuZQJzRa … ca9z',
                '/ip4/104.236.179.241/tcp/4001/ipfs/QmSoLPppuBtQSGwKD … KrGM',
                …
                '/ip4/178.62.61.185/tcp/4001/ipfs/QmSoLMeWqB7YGVLJN3p … QBU3']}

        Returns
        -------
            dict : List of known bootstrap peers
        """
        return self._bootstrap.request(self._client, **kwargs)

    def bootstrap_add(self, peer, *peers, **kwargs):
        """Adds peers to the bootstrap list.

        Parameters
        ----------
        peer : str
            IPFS MultiAddr of a peer to add to the list

        Returns
        -------
            dict
        """
        return self._bootstrap_add.request(
            self._client, peer, *peers, **kwargs
        )

    def bootstrap_rm(self, peer, *peers, **kwargs):
        """Removes peers from the bootstrap list.

        Parameters
        ----------
        peer : str
            IPFS MultiAddr of a peer to remove from the list

        Returns
        -------
            dict
        """
        return self._bootstrap_rm.request(
            self._client, peer, *peers, **kwargs
        )

    def swarm_peers(self, **kwargs):
        """Returns the addresses & IDs of currently connected peers.

        .. code-block:: python

            >>> c.swarm_peers()
            {'Strings': [
                '/ip4/101.201.40.124/tcp/40001/ipfs/QmZDYAhmMDtnoC6XZ … kPZc',
                '/ip4/104.131.131.82/tcp/4001/ipfs/QmaCpDMGvV2BGHeYER … uvuJ',
                '/ip4/104.223.59.174/tcp/4001/ipfs/QmeWdgoZezpdHz1PX8 … 1jB6',
                …
                '/ip6/fce3: … :f140/tcp/43901/ipfs/QmSoLnSGccFuZQJzRa … ca9z']}

        Returns
        -------
            dict : List of multiaddrs of currently connected peers
        """
        return self._swarm_peers.request(self._client, **kwargs)

    def swarm_addrs(self, **kwargs):
        """Returns the addresses of currently connected peers by peer id.

        .. code-block:: python

            >>> pprint(c.swarm_addrs())
            {'Addrs': {
                'QmNMVHJTSZHTWMWBbmBrQgkA1hZPWYuVJx2DpSGESWW6Kn': [
                    '/ip4/10.1.0.1/tcp/4001',
                    '/ip4/127.0.0.1/tcp/4001',
                    '/ip4/51.254.25.16/tcp/4001',
                    '/ip6/2001:41d0:b:587:3cae:6eff:fe40:94d8/tcp/4001',
                    '/ip6/2001:470:7812:1045::1/tcp/4001',
                    '/ip6/::1/tcp/4001',
                    '/ip6/fc02:2735:e595:bb70:8ffc:5293:8af8:c4b7/tcp/4001',
                    '/ip6/fd00:7374:6172:100::1/tcp/4001',
                    '/ip6/fd20:f8be:a41:0:c495:aff:fe7e:44ee/tcp/4001',
                    '/ip6/fd20:f8be:a41::953/tcp/4001'],
                'QmNQsK1Tnhe2Uh2t9s49MJjrz7wgPHj4VyrZzjRe8dj7KQ': [
                    '/ip4/10.16.0.5/tcp/4001',
                    '/ip4/127.0.0.1/tcp/4001',
                    '/ip4/172.17.0.1/tcp/4001',
                    '/ip4/178.62.107.36/tcp/4001',
                    '/ip6/::1/tcp/4001'],
                …
            }}

        Returns
        -------
            dict : Multiaddrs of peers by peer id
        """
        return self._swarm_addrs.request(self._client, **kwargs)

    def swarm_connect(self, address, *addresses, **kwargs):
        """Opens a connection to a given address.

        This will open a new direct connection to a peer address. The address
        format is an IPFS multiaddr::

            /ip4/104.131.131.82/tcp/4001/ipfs/QmaCpDMGvV2BGHeYERUEnRQAwe3N8SzbUtfsmvsqQLuvuJ

        .. code-block:: python

            >>> c.swarm_connect("/ip4/104.131.131.82/tcp/4001/ipfs/Qma … uvuJ")
            {'Strings': ['connect QmaCpDMGvV2BGHeYERUEnRQAwe3 … uvuJ success']}

        Parameters
        ----------
        address : str
            Address of peer to connect to

        Returns
        -------
            dict : Textual connection status report
        """
        return self._swarm_connecti.request(
            self._client, address, *addresses, **kwargs
        )

    def swarm_disconnect(self, address, *addresses, **kwargs):
        """Closes the connection to a given address.

        This will close a connection to a peer address. The address format is
        an IPFS multiaddr::

            /ip4/104.131.131.82/tcp/4001/ipfs/QmaCpDMGvV2BGHeYERUEnRQAwe3N8SzbUtfsmvsqQLuvuJ

        The disconnect is not permanent; if IPFS needs to talk to that address
        later, it will reconnect.

        .. code-block:: python

            >>> c.swarm_disconnect("/ip4/104.131.131.82/tcp/4001/ipfs/Qm … uJ")
            {'Strings': ['disconnect QmaCpDMGvV2BGHeYERUEnRQA … uvuJ success']}

        Parameters
        ----------
        address : str
            Address of peer to disconnect from

        Returns
        -------
            dict : Textual connection status report
        """
        return self._swarm_disconnect.request(
            self._client, address, *addresses, **kwargs
        )

    def swarm_filters_add(self, address, *addresses, **kwargs):
        """Adds a given multiaddr filter to the filter list.

        This will add an address filter to the daemons swarm. Filters applied
        this way will not persist daemon reboots, to achieve that, add your
        filters to the configuration file.

        .. code-block:: python

            >>> c.swarm_filters_add("/ip4/192.168.0.0/ipcidr/16")
            {'Strings': ['/ip4/192.168.0.0/ipcidr/16']}

        Parameters
        ----------
        address : str
            Multiaddr to filter

        Returns
        -------
            dict : List of swarm filters added
        """
        return self._swarm_filters_add.request(
            self._client, address, *addresses, **kwargs
        )

    def swarm_filters_rm(self, address, *addresses, **kwargs):
        """Removes a given multiaddr filter from the filter list.

        This will remove an address filter from the daemons swarm. Filters
        removed this way will not persist daemon reboots, to achieve that,
        remove your filters from the configuration file.

        .. code-block:: python

            >>> c.swarm_filters_rm("/ip4/192.168.0.0/ipcidr/16")
            {'Strings': ['/ip4/192.168.0.0/ipcidr/16']}

        Parameters
        ----------
        address : str
            Multiaddr filter to remove

        Returns
        -------
            dict : List of swarm filters removed
        """
        return self._swarm_filters_rm.request(
            self._client, address, *addresses, **kwargs
        )

    def dht_query(self, peer_id, *peer_ids, **kwargs):
        """Finds the closest Peer IDs to a given Peer ID by querying the DHT.

        .. code-block:: python

            >>> c.dht_query("/ip4/104.131.131.82/tcp/4001/ipfs/QmaCpDM … uvuJ")
            [{'ID': 'QmPkFbxAQ7DeKD5VGSh9HQrdS574pyNzDmxJeGrRJxoucF',
              'Extra': '', 'Type': 2, 'Responses': None},
             {'ID': 'QmR1MhHVLJSLt9ZthsNNhudb1ny1WdhY4FPW21ZYFWec4f',
              'Extra': '', 'Type': 2, 'Responses': None},
             {'ID': 'Qmcwx1K5aVme45ab6NYWb52K2TFBeABgCLccC7ntUeDsAs',
              'Extra': '', 'Type': 2, 'Responses': None},
             …
             {'ID': 'QmYYy8L3YD1nsF4xtt4xmsc14yqvAAnKksjo3F3iZs5jPv',
              'Extra': '', 'Type': 1, 'Responses': []}]

        Parameters
        ----------
        peer_id : str
            The peerID to run the query against

        Returns
        -------
            dict : List of peers IDs
        """
        return self._dht_query.request(
            self._client, peer_id, *peer_ids, **kwargs
        )

    def dht_findprovs(self, multihash, *multihashes, **kwargs):
        """Finds peers in the DHT that can provide a specific value.

        .. code-block:: python

            >>> c.dht_findprovs("QmNPXDC6wTXVmZ9Uoc8X1oqxRRJr4f1sDuyQu … mpW2")
            [{'ID': 'QmaxqKpiYNr62uSFBhxJAMmEMkT6dvc3oHkrZNpH2VMTLZ',
              'Extra': '', 'Type': 6, 'Responses': None},
             {'ID': 'QmaK6Aj5WXkfnWGoWq7V8pGUYzcHPZp4jKQ5JtmRvSzQGk',
              'Extra': '', 'Type': 6, 'Responses': None},
             {'ID': 'QmdUdLu8dNvr4MVW1iWXxKoQrbG6y1vAVWPdkeGK4xppds',
              'Extra': '', 'Type': 6, 'Responses': None},
             …
             {'ID': '', 'Extra': '', 'Type': 4, 'Responses': [
                {'ID': 'QmVgNoP89mzpgEAAqK8owYoDEyB97Mk … E9Uc', 'Addrs': None}
              ]},
             {'ID': 'QmaxqKpiYNr62uSFBhxJAMmEMkT6dvc3oHkrZNpH2VMTLZ',
              'Extra': '', 'Type': 1, 'Responses': [
                {'ID': 'QmSHXfsmN3ZduwFDjeqBn1C8b1tcLkxK6yd … waXw', 'Addrs': [
                    '/ip4/127.0.0.1/tcp/4001',
                    '/ip4/172.17.0.8/tcp/4001',
                    '/ip6/::1/tcp/4001',
                    '/ip4/52.32.109.74/tcp/1028'
                  ]}
              ]}]

        Parameters
        ----------
        multihash : str
            The DHT key to find providers for

        Returns
        -------
            dict : List of provider Peer IDs
        """
        return self._dht_findprovs.request(
            self._client, multihash, *multihashes, **kwargs
        )

    def dht_findpeer(self, peer_id, *peer_ids, **kwargs):
        """Queries the DHT for all of the associated multiaddresses.

        .. code-block:: python

            >>> c.dht_findpeer("QmaxqKpiYNr62uSFBhxJAMmEMkT6dvc3oHkrZN … MTLZ")
            [{'ID': 'QmfVGMFrwW6AV6fTWmD6eocaTybffqAvkVLXQEFrYdk6yc',
              'Extra': '', 'Type': 6, 'Responses': None},
             {'ID': 'QmTKiUdjbRjeN9yPhNhG1X38YNuBdjeiV9JXYWzCAJ4mj5',
              'Extra': '', 'Type': 6, 'Responses': None},
             {'ID': 'QmTGkgHSsULk8p3AKTAqKixxidZQXFyF7mCURcutPqrwjQ',
              'Extra': '', 'Type': 6, 'Responses': None},
             …
             {'ID': '', 'Extra': '', 'Type': 2,
              'Responses': [
                {'ID': 'QmaxqKpiYNr62uSFBhxJAMmEMkT6dvc3oHkrZNpH2VMTLZ',
                 'Addrs': [
                    '/ip4/10.9.8.1/tcp/4001',
                    '/ip6/::1/tcp/4001',
                    '/ip4/164.132.197.107/tcp/4001',
                    '/ip4/127.0.0.1/tcp/4001']}
              ]}]

        Parameters
        ----------
        peer_id : str
            The ID of the peer to search for

        Returns
        -------
            dict : List of multiaddrs
        """
        return self._dht_findpeer.request(
            self._client, peer_id, *peer_ids, **kwargs
        )

    def dht_get(self, key, *keys, **kwargs):
        """Queries the DHT for its best value related to given key.

        There may be several different values for a given key stored in the
        DHT; in this context *best* means the record that is most desirable.
        There is no one metric for *best*: it depends entirely on the key type.
        For IPNS, *best* is the record that is both valid and has the highest
        sequence number (freshest). Different key types may specify other rules
        for they consider to be the *best*.

        Parameters
        ----------
        key : str
            One or more keys whose values should be looked up

        Returns
        -------
            str
        """
        res = self._dht_get.request(self._client, key, *keys, **kwargs)
        if isinstance(res, dict) and "Extra" in res:
            return res["Extra"]
        else:
            for r in res:
                if "Extra" in r and len(r["Extra"]) > 0:
                    return r["Extra"]
        raise exceptions.Error("empty response from DHT")

    def dht_put(self, key, value, **kwargs):
        """Writes a key/value pair to the DHT.

        Given a key of the form ``/foo/bar`` and a value of any form, this will
        write that value to the DHT with that key.

        Keys have two parts: a keytype (foo) and the key name (bar). IPNS uses
        the ``/ipns/`` keytype, and expects the key name to be a Peer ID. IPNS
        entries are formatted with a special strucutre.

        You may only use keytypes that are supported in your ``ipfs`` binary:
        ``go-ipfs`` currently only supports the ``/ipns/`` keytype. Unless you
        have a relatively deep understanding of the key's internal structure,
        you likely want to be using the :meth:`~ipfsApi.Client.name_publish`
        instead.

        Value is arbitrary text.

        .. code-block:: python

            >>> c.dht_put("QmVgNoP89mzpgEAAqK8owYoDEyB97Mkc … E9Uc", "test123")
            [{'ID': 'QmfLy2aqbhU1RqZnGQyqHSovV8tDufLUaPfN1LNtg5CvDZ',
              'Extra': '', 'Type': 5, 'Responses': None},
             {'ID': 'QmZ5qTkNvvZ5eFq9T4dcCEK7kX8L7iysYEpvQmij9vokGE',
              'Extra': '', 'Type': 5, 'Responses': None},
             {'ID': 'QmYqa6QHCbe6eKiiW6YoThU5yBy8c3eQzpiuW22SgVWSB8',
              'Extra': '', 'Type': 6, 'Responses': None},
             …
             {'ID': 'QmP6TAKVDCziLmx9NV8QGekwtf7ZMuJnmbeHMjcfoZbRMd',
              'Extra': '', 'Type': 1, 'Responses': []}]

        Parameters
        ----------
        key : str
            A unique identifier
        value : str
            Abitrary text to associate with the input (2048 bytes or less)

        Returns
        -------
            list
        """
        return self._dht_put.request(self._client, key, value, **kwargs)

    def ping(self, peer, *peers, **kwargs):
        """Provides round-trip latency information for the routing system.

        Finds nodes via the routing system, sends pings, waits for pongs,
        and prints out round-trip latency information.

        .. code-block:: python

            >>> c.ping("QmTzQ1JRkWErjk39mryYw2WVaphAZNAREyMchXzYQ7c15n")
            [{'Success': True,  'Time': 0,
              'Text': 'Looking up peer QmTzQ1JRkWErjk39mryYw2WVaphAZN … c15n'},
             {'Success': False, 'Time': 0,
              'Text': 'Peer lookup error: routing: not found'}]

        Parameters
        ----------
        peer : str
            ID of peer to be pinged
        count : int
            Number of ping messages to send (Default: ``10``)

        Returns
        -------
            list : Progress reports from the ping
        """
        # Python 2 does not support kw-only parameters after glob parameters
        if "count" in kwargs:
            kwargs.setdefault("opts", {"count": kwargs["count"]})
            del kwargs["count"]

        return self._ping.request(self._client, peer, *peers, **kwargs)

    def config(self, key, value=None, *args, **kwargs):
        """Controls configuration variables.

        .. code-block:: python

            >>> c.config("Addresses.Gateway")
            {'Key': 'Addresses.Gateway', 'Value': '/ip4/127.0.0.1/tcp/8080'}
            >>> c.config("Addresses.Gateway", "/ip4/127.0.0.1/tcp/8081")
            {'Key': 'Addresses.Gateway', 'Value': '/ip4/127.0.0.1/tcp/8081'}

        Parameters
        ----------
        key : str
            The key of the configuration entry (e.g. "Addresses.API")
        value : dict
            The value to set the configuration entry to

        Returns
        -------
            dict : Requested/updated key and its (new) value
        """
        return self._config.request(self._client, key, value, *args, **kwargs)

    def config_show(self, **kwargs):
        """Returns a dict containing the server's configuration.

        .. warning::

            The configuration file contains private key data that must be
            handled with care.

        .. code-block:: python

            >>> config = c.config_show()
            >>> config['Addresses']
            {'API': '/ip4/127.0.0.1/tcp/5001',
             'Gateway': '/ip4/127.0.0.1/tcp/8080',
             'Swarm': ['/ip4/0.0.0.0/tcp/4001', '/ip6/::/tcp/4001']},
            >>> config['Discovery']
            {'MDNS': {'Enabled': True, 'Interval': 10}}

        Returns
        -------
            dict : The entire IPFS daemon configuration
        """
        return self._config_show.request(self._client, **kwargs)

    def config_replace(self, *args, **kwargs):
        """Replaces the existing config with a user-defined config.

        Make sure to back up the config file first if neccessary, as this
        operation can't be undone.
        """
        return self._config_replace.request(self._client, *args, **kwargs)

    def log_level(self, subsystem, level, **kwargs):
        r"""Changes the logging output of a running daemon.

        .. code-block:: python

            >>> c.log_level("path", "info")
            {'Message': "Changed log level of 'path' to 'info'\n"}

        Parameters
        ----------
        subsystem : str
            The subsystem logging identifier (Use ``"all"`` for all subsystems)
        level : str
            The desired logging level. Must be one of:

             * ``"debug"``
             * ``"info"``
             * ``"warning"``
             * ``"error"``
             * ``"fatal"``
             * ``"panic"``

        Returns
        -------
            dict : Status message
        """
        return self._log_level.request(self._client, subsystem,
                                       level, **kwargs)

    def log_ls(self, **kwargs):
        """Lists the logging subsystems of a running daemon.

        .. code-block:: python

            >>> c.log_ls()
            {'Strings': [
                'github.com/ipfs/go-libp2p/p2p/host', 'net/identify',
                'merkledag', 'providers', 'routing/record', 'chunk', 'mfs',
                'ipns-repub', 'flatfs', 'ping', 'mockrouter', 'dagio',
                'cmds/files', 'blockset', 'engine', 'mocknet', 'config',
                'commands/http', 'cmd/ipfs', 'command', 'conn', 'gc',
                'peerstore', 'core', 'coreunix', 'fsrepo', 'core/server',
                'boguskey', 'github.com/ipfs/go-libp2p/p2p/host/routed',
                'diagnostics', 'namesys', 'fuse/ipfs', 'node', 'secio',
                'core/commands', 'supernode', 'mdns', 'path', 'table',
                'swarm2', 'peerqueue', 'mount', 'fuse/ipns', 'blockstore',
                'github.com/ipfs/go-libp2p/p2p/host/basic', 'lock', 'nat',
                'importer', 'corerepo', 'dht.pb', 'pin', 'bitswap_network',
                'github.com/ipfs/go-libp2p/p2p/protocol/relay', 'peer',
                'transport', 'dht', 'offlinerouting', 'tarfmt', 'eventlog',
                'ipfsaddr', 'github.com/ipfs/go-libp2p/p2p/net/swarm/addr',
                'bitswap', 'reprovider', 'supernode/proxy', 'crypto', 'tour',
                'commands/cli', 'blockservice']}

        Returns
        -------
            dict : List of daemon logging subsystems
        """
        return self._log_ls.request(self._client, **kwargs)

    def log_tail(self, **kwargs):
        r"""Reads log outputs as they are written.

        This function returns a reponse object that can be iterated over
        by the user. The user should make sure to close the response object
        when they are done reading from it.

        .. code-block:: python

            >>> for item in c.log_tail():
            ...     print(item)
            ...
            b'{"event":"updatePeer","system":"dht",
               "peerID":"QmepsDPxWtLDuKvEoafkpJxGij4kMax11uTH7WnKqD25Dq",
               "session":"7770b5e0-25ec-47cd-aa64-f42e65a10023",
               "time":"2016-08-22T13:25:27.43353297Z"}\n'
            b'{"event":"handleAddProviderBegin","system":"dht",
               "peer":"QmepsDPxWtLDuKvEoafkpJxGij4kMax11uTH7WnKqD25Dq",
               "session":"7770b5e0-25ec-47cd-aa64-f42e65a10023",
               "time":"2016-08-22T13:25:27.433642581Z"}\n'
            b'{"event":"handleAddProvider","system":"dht","duration":91704,
               "key":"QmNT9Tejg6t57Vs8XM2TVJXCwevWiGsZh3kB4HQXUZRK1o",
               "peer":"QmepsDPxWtLDuKvEoafkpJxGij4kMax11uTH7WnKqD25Dq",
               "session":"7770b5e0-25ec-47cd-aa64-f42e65a10023",
               "time":"2016-08-22T13:25:27.433747513Z"}\n'
            b'{"event":"updatePeer","system":"dht",
               "peerID":"QmepsDPxWtLDuKvEoafkpJxGij4kMax11uTH7WnKqD25Dq",
               "session":"7770b5e0-25ec-47cd-aa64-f42e65a10023",
               "time":"2016-08-22T13:25:27.435843012Z"}\n
            …

        Returns
        -------
            iterable
        """
        return self._log_tail.request(self._client, stream=True, **kwargs)

    def version(self, **kwargs):
        """Returns the software version of the currently connected node.

        .. code-block:: python

            >>> c.version()
            {'Version': '0.4.3-rc2', 'Repo': '4', 'Commit': '',
             'System': 'amd64/linux', 'Golang': 'go1.6.2'}

        Returns
        -------
            dict : Daemon and system version information
        """
        return self._version.request(self._client, **kwargs)

    def files_cp(self, source, dest, **kwargs):
        """Copies files within the MFS.

        Due to the nature of IPFS this will not actually involve any of the
        file's content being copied.

        .. code-block:: python

            >>> c.files_ls("/")
            {'Entries': [
                {'Size': 0, 'Hash': '', 'Name': 'Software', 'Type': 0},
                {'Size': 0, 'Hash': '', 'Name': 'test', 'Type': 0}
            ]}
            >>> c.files_cp("/test", "/bla")
            ''
            >>> c.files_ls("/")
            {'Entries': [
                {'Size': 0, 'Hash': '', 'Name': 'Software', 'Type': 0},
                {'Size': 0, 'Hash': '', 'Name': 'bla', 'Type': 0},
                {'Size': 0, 'Hash': '', 'Name': 'test', 'Type': 0}
            ]}

        Parameters
        ----------
        source : str
            Filepath within the MFS to copy from
        dest : str
            Destination filepath with the MFS to which the file will be
            copied to
        """
        return self._files_cp.request(self._client, source, dest, **kwargs)

    def files_ls(self, path, **kwargs):
        """Lists contents of a directory in the MFS.

        .. code-block:: python

            >>> c.files_ls("/")
            {'Entries': [
                {'Size': 0, 'Hash': '', 'Name': 'Software', 'Type': 0}
            ]}

        Parameters
        ----------
        path : str
            Filepath within the MFS

        Returns
        -------
            dict : Directory entries
        """
        return self._files_ls.request(self._client, path, **kwargs)

    def files_mkdir(self, path, parents=False, **kwargs):
        """Creates a directory within the MFS.

        .. code-block:: python

            >>> c.files_mkdir("/test")
            b''

        Parameters
        ----------
        path : str
            Filepath within the MFS
        parents : bool
            Create parent directories as needed and do not raise an exception
            if the requested directory already exists
        """
        kwargs.setdefault("opts", {"parents": parents})
        return self._files_mkdir.request(self._client, path, **kwargs)

    def files_stat(self, path, **kwargs):
        """Returns basic ``stat`` information for an MFS file
        (including its hash).

        .. code-block:: python

            >>> c.files_stat("/test")
            {'Hash': 'QmUNLLsPACCz1vLxQVkXqqLX5R1X345qqfHbsf67hvA3Nn',
             'Size': 0, 'CumulativeSize': 4, 'Type': 'directory', 'Blocks': 0}

        Parameters
        ----------
        path : str
            Filepath within the MFS

        Returns
        -------
            dict : MFS file information
        """
        return self._files_stat.request(self._client, path, **kwargs)

    def files_rm(self, path, recursive=False, **kwargs):
        """Removes a file from the MFS.

        .. code-block:: python

            >>> c.files_rm("/bla/file")
            b''

        Parameters
        ----------
        path : str
            Filepath within the MFS
        recursive : bool
            Recursively remove directories?
        """
        kwargs.setdefault("opts", {"recursive": recursive})
        return self._files_rm.request(self._client, path, **kwargs)

    def files_read(self, path, offset=0, count=None, **kwargs):
        """Reads a file stored in the MFS.

        .. code-block:: python

            >>> c.files_read("/bla/file")
            b'hi'

        Parameters
        ----------
        path : str
            Filepath within the MFS
        offset : int
            Byte offset at which to begin reading at
        count : int
            Maximum number of bytes to read

        Returns
        -------
            str : MFS file contents
        """
        opts = {"offset": offset}
        if count is not None:
            opts["count"] = count

        kwargs.setdefault("opts", opts)
        return self._files_read.request(self._client, path, **kwargs)

    def files_write(self, path, file, offset=0, create=False, truncate=False,
                    count=None, **kwargs):
        """Writes to a mutable file in the MFS.

        .. code-block:: python

            >>> c.files_write("/test/file", io.BytesIO(b"hi"), create=True)
            b''

        Parameters
        ----------
        path : str
            Filepath within the MFS
        file : io.RawIOBase
            IO stream object with data that should be written
        offset : int
            Byte offset at which to begin writing at
        create : bool
            Create the file if it does not exist
        truncate : bool
            Truncate the file to size zero before writing
        count : int
            Maximum number of bytes to read from the source ``file``
        """
        opts = {"offset": offset, "create": create, truncate: truncate}
        if count is not None:
            opts["count"] = count

        kwargs.setdefault("opts", opts)
        return self._files_write.request(self._client, (path,), file, **kwargs)

    def files_mv(self, source, dest, **kwargs):
        """Moves files and directories within the MFS.

        .. code-block:: python

            >>> c.files_mv("/test/file", "/bla/file")
            b''

        Parameters
        ----------
        source : str
            Existing filepath within the MFS
        dest : str
            Destination to which the file will be moved in the MFS
        """
        return self._files_mv.request(self._client, source, dest, **kwargs)

    ###########
    # HELPERS #
    ###########

    @utils.return_field('Hash')
    def add_bytes(self, data, **kwargs):
        """Adds a set of bytes as a file to IPFS.

        .. code-block:: python

            >>> c.add_bytes(b"Mary had a little lamb")
            'QmZfF6C9j4VtoCsTp4KSrhYH47QMd3DNXVZBKaxJdhaPab'

        Also accepts and will stream generator objects.

        Parameters
        ----------
        data : bytes
            Content to be added as a file

        Returns
        -------
            str : Hash of the added IPFS object
        """
        chunk_size = kwargs.pop('chunk_size', multipart.default_chunk_size)
        body, headers = multipart.stream_bytes(data, chunk_size=chunk_size)
        return self._client.request('/add', data=body,
                                    headers=headers, **kwargs)

    @utils.return_field('Hash')
    def add_str(self, string, **kwargs):
        """Adds a Python string as a file to IPFS.

        .. code-block:: python

            >>> c.add_str(u"Mary had a little lamb")
            'QmZfF6C9j4VtoCsTp4KSrhYH47QMd3DNXVZBKaxJdhaPab'

        Also accepts and will stream generator objects.

        Parameters
        ----------
        string : str
            Content to be added as a file

        Returns
        -------
            str : Hash of the added IPFS object
        """
        chunk_size = kwargs.pop('chunk_size', multipart.default_chunk_size)
        body, headers = multipart.stream_text(string, chunk_size=chunk_size)
        return self._client.request('/add', data=body,
                                    headers=headers, **kwargs)

    def add_json(self, json_obj, **kwargs):
        """Adds a json-serializable Python dict as a json file to IPFS.

        .. code-block:: python

            >>> c.add_json({'one': 1, 'two': 2, 'three': 3})
            'QmVz9g7m5u3oHiNKHj2CJX1dbG1gtismRS3g9NaPBBLbob'

        Parameters
        ----------
        json_obj : dict
            A json-serializable Python dictionary

        Returns
        -------
            str : Hash of the added IPFS object
        """
        return self.add_bytes(encoding.Json().encode(json_obj), **kwargs)

    def get_json(self, multihash, **kwargs):
        """Loads a json object from IPFS.

        .. code-block:: python

            >>> c.get_json('QmVz9g7m5u3oHiNKHj2CJX1dbG1gtismRS3g9NaPBBLbob')
            {'one': 1, 'two': 2, 'three': 3}

        Parameters
        ----------
        multihash : str
           Multihash of the IPFS object to load

        Returns
        -------
            object : Deserialized IPFS JSON object value
        """
        return self.cat(multihash, decoder='json', **kwargs)

    def add_pyobj(self, py_obj, **kwargs):
        """Adds a picklable Python object as a file to IPFS.

        .. code-block:: python

            >>> c.add_pyobj([0, 1.0, 2j, '3', 4e5])
            'QmWgXZSUTNNDD8LdkdJ8UXSn55KfFnNvTP1r7SyaQd74Ji'

        Parameters
        ----------
        py_obj : object
            A picklable Python object

        Returns
        -------
            str : Hash of the added IPFS object
        """
        return self.add_bytes(encoding.Pickle().encode(py_obj), **kwargs)

    def get_pyobj(self, multihash, **kwargs):
        """Loads a pickled Python object from IPFS.

        .. caution::

            The pickle module is not intended to be secure against erroneous or
            maliciously constructed data. Never unpickle data received from an
            untrusted or unauthenticated source.

            See the :mod:`pickle` module documentation for more information.

        .. code-block:: python

            >>> c.get_pyobj('QmWgXZSUTNNDD8LdkdJ8UXSn55KfFnNvTP1r7SyaQd74Ji')
            [0, 1.0, 2j, '3', 400000.0]

        Parameters
        ----------
        multihash : str
            Multihash of the IPFS object to load

        Returns
        -------
            object : Deserialized IPFS Python object
        """
        return self.cat(multihash, decoder='pickle', **kwargs)
