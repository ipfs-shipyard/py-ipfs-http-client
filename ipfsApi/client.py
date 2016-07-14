"""IPFS API Bindings for Python.

Classes:
Client -- a TCP client for interacting with an IPFS daemon
"""
from __future__ import absolute_import

from . import http, multipart, utils
from .commands import ArgCommand, Command, DownloadCommand, FileCommand
from .exceptions import ipfsApiError

default_host = 'localhost'
default_port = 5001
default_base = 'api/v0'


class Client(object):
    """A TCP client for interacting with an IPFS daemon.

    Public methods:
    __init__ -- connects to the API port of an IPFS node
    add -- add a file, or directory of files to IPFS
    get -- downloads a file, or directory of files from IPFS to the current
           working directory
    cat -- returns the contents of a file identified by hash, as a string
    ls -- returns a list of objects linked to the given hash
    refs -- returns a list of hashes of objects referenced by the given hash
    block_stat -- returns a dict with the size of the block with the given hash
    block_get -- returns the raw contents of a block
    block_put -- stores input as an IPFS block
    object_data -- returns the raw bytes in an IPFS object
    object_new -- creates a new object from an ipfs template
    object_links -- returns the links pointed to by the specified object
    object_get -- get and serialize the DAG node named by multihash
    object_put -- stores input as a DAG object and returns its key
    object_stat -- get stats for the DAG node named by multihash
    object_patch -- create a new merkledag object based on an existing one
    file_ls -- lists directory contents for Unix filesystem objects
    resolve -- accepts an identifier and resolves it to the referenced item
    name_publish -- publishes an object to IPNS
    name_resolve -- gets the value currently published at an IPNS name
    dns -- resolves DNS links to the referenced object
    pin_add -- pins objects to local storage
    pin_rm -- removes a pinned object from local storage
    pin_ls -- lists objects pinned to local storage
    repo_gc -- removes stored objects that are not pinned from the repo
    id -- shows IPFS Node ID info
    bootstrap -- shows peers in the bootstrap list
    bootstrap_add -- adds peers to the bootstrap list
    bootstrap_rm -- removes peers from the bootstrap list
    swarm_peers -- returns the addresses & IDs of currently connected peers
    swarm_addrs -- returns the addresses of currently connected peers
                   by peer id
    swarm_connect -- opens a connection to a given address
    swarm_disconnect -- closes the connection to a given address
    swarm_filters_add -- adds a given multiaddr filter to the filter list
    swarm_filters_rm -- removes a given multiaddr filter from the filter list
    dht_query -- finds the closest Peer IDs to a given Peer ID by
                 querying the DHT
    dht_findprovs -- finds peers in the DHT that can provide a specific value,
                     given a key
    dht_findpeer -- queries the DHT for all of the multiaddresses associated
                    with a Peer ID
    dht_get -- queries the DHT for its best value related to given key
    dht_put -- writes a key/value pair to the DHT
    ping -- provides round-trip latency information for the routing system
    config -- controls configuration variables
    config_show -- returns a dict containing the server's configuration
    config_replace -- replaces the existing config with a user-defined config
    version -- returns the software version of the currently connected node
    files_cp -- copies files into MFS
    files_ls -- lists directory contents in MFS
    files_mkdir -- creates a directory in MFS
    files_stat -- displays a file's status (including it's hash) in MFS
    files_rm -- removes a file from MFS
    files_read -- reads a file stored in MFS
    files_write -- writes to a mutable file in MFS
    files_mv -- moves MFS files
    add_str -- adds a Python string as a file to IPFS
    add_json -- adds a json-serializable Python dict as a json file to IPFS
    get_json -- loads a json object from IPFS
    add_pyobj -- adds a picklable Python object as a file to IPFS
    get_pyobj -- loads a pickled Python object from IPFS
    """

    _clientfactory = http.HTTPClient

    def __init__(self, host=None, port=None,
                 base=None, default_enc='json', **defaults):
        """Connects to the API port of an IPFS node."""
        if host is None:
            host = default_host
        if port is None:
            port = default_port
        if base is None:
            base = default_base

        self._client = self._clientfactory(host, port, base,
                                           default_enc, **defaults)

        # BASIC COMMANDS
        self._add                = FileCommand('/add')
        self._get                = DownloadCommand('/get')
        self._cat                = ArgCommand('/cat')
        self._ls                 = ArgCommand('/ls')
        self._refs               = ArgCommand('/refs')

        # DATA STRUCTURE COMMANDS
        self._block_stat         = ArgCommand('/block/stat')
        self._block_get          = ArgCommand('/block/get')
        self._block_put          = FileCommand('/block/put')
        self._object_data        = ArgCommand('/object/data')
        self._object_links       = ArgCommand('/object/links')
        self._object_get         = ArgCommand('/object/get')
        self._object_put         = FileCommand('/object/put')
        self._object_stat        = ArgCommand('/object/stat')
        self._object_patch       = ArgCommand('/object/patch')
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

        >> with io.open('nurseryrhyme.txt', 'w', encoding='utf-8') as f:
        ...     numbytes = f.write(u'Mary had a little lamb')
        >> c.add('nurseryrhyme.txt')
        {u'Hash': u'QmZfF6C9j4VtoCsTp4KSrhYH47QMd3DNXVZBKaxJdhaPab',
         u'Name': u'nurseryrhyme.txt'}

         Keyword arguments:
         files -- a filepath to either a file or directory
         recursive -- controls if files in subdirectories are added or not
         kwargs -- additional named arguments
        """
        return self._add.request(self._client, (), files,
                                 recursive=recursive, **kwargs)

    def get(self, multihash, **kwargs):
        """Downloads a file, or directory of files from IPFS.

        Files are placed in the current working directory.

        Keyword arguments:
        multihash -- unique checksum used to identify IPFS resources
        kwargs -- additional named arguments
        """
        return self._get.request(self._client, multihash, **kwargs)

    def cat(self, multihash, **kwargs):
        r"""Returns the contents of a file identified by hash, as a string.

        >> c.cat('QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDxdXBFca7D')
        Traceback (most recent call last):
          ...
        ipfsApiError: this dag node is a directory
        >> c.cat('QmeKozNssnkJ4NcyRidYgDY2jfRZqVEoRGfipkgath71bX')[:60]
        u'<!DOCTYPE html>\n<html>\n\n<head>\n<title>ipfs example viewer</t'

        Keyword arguments:
        multihash -- unique checksum used to identify IPFS resources
        kwargs -- additional named arguments
        """
        return self._cat.request(self._client, multihash, **kwargs)

    def ls(self, multihash, **kwargs):
        """Returns a list of objects linked to the given hash.

        >> c.ls('QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDxdXBFca7D')
        {u'Objects': [
            {u'Hash': u'QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDxdXBFca7D',
             u'Links': [
                {u'Hash': u'Qmd2xkBfEwEs9oMTk77A6jrsgurpF3ugXSg7dtPNFkcNMV',
                 u'Name': u'Makefile', u'Size': 174, u'Type': 2},
                 ...
                {u'Hash': u'QmSY8RfVntt3VdxWppv9w5hWgNrE31uctgTiYwKir8eXJY',
                 u'Name': u'published-version', u'Size': 55, u'Type': 2}
                ]}
            ]}

        Keyword arguments:
        multihash -- unique checksum used to identify IPFS resources
        kwargs -- additional named arguments
        """
        return self._ls.request(self._client, multihash, **kwargs)

    def refs(self, multihash, **kwargs):
        """Returns a list of hashes of objects referenced by the given hash.

        >> c.refs('QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDxdXBFca7D')
        [{u'Ref': u'Qmd2xkBfEwEs9oMTk77A6jrsgurpF3ugXSg7dtPNFkcNMV',
          u'Err': u''},
         ...
         {u'Ref': u'QmSY8RfVntt3VdxWppv9w5hWgNrE31uctgTiYwKir8eXJY',
         u'Err': u''}]

        Keyword arguments:
        multihash -- unique checksum used to identify IPFS resources
        kwargs -- additional named arguments
        """
        return self._refs.request(self._client, multihash, **kwargs)

    def block_stat(self, multihash, **kwargs):
        """Returns a dict with the size of the block with the given hash.

        >> c.block_stat('QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDxdXBFca7D')
        {u'Key': u'QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDxdXBFca7D',
         u'Size': 258}

        Keyword arguments:
        multihash -- unique checksum used to identify IPFS resources
        kwargs -- additional named arguments
        """
        return self._block_stat.request(self._client, multihash, **kwargs)

    def block_get(self, multihash, **kwargs):
        r"""Returns the raw contents of a block.

        >> c.block_get('QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDxdXBFca7D')
        u'\x121\n"\x12 \xdaW> ... \x11published-version\x187\n\x02\x08\x01'

        Keyword arguments:
        multihash -- unique checksum used to identify IPFS resources
        kwargs -- additional named arguments
        """
        return self._block_get.request(self._client, multihash, **kwargs)

    def block_put(self, file, **kwargs):
        """Stores input as an IPFS block.

        >> c.block_put(io.StringIO(u'Mary had a little lamb'))
        {u'Key': u'QmeV6C6XVt1wf7V7as7Yak3mxPma8jzpqyhtRtCvpKcfBb',
         u'Size': 22}

        Keyword arguments:
        file -- object to be stored
        kwargs -- additional named arguments
        """
        return self._block_put.request(self._client, (), file, **kwargs)

    def object_data(self, multihash, **kwargs):
        r"""Returns the raw bytes in an IPFS object.

        >> c.object_data('QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDxdXBFca7D')
        u'\x08\x01'

        Keyword arguments:
        multihash -- unique checksum used to identify IPFS resources
        kwargs -- additional named arguments
        """
        return self._object_data.request(self._client, multihash, **kwargs)

    def object_new(self, template=None, **kwargs):
        """Creates a new object from an IPFS template.

        By default it creates and returns a new empty merkledag node, but you
        may pass an optional template argument to create a preformatted node.

        >> c.object_new()
        {u'Hash': u'QmdfTbBqBPQ7VNxZEYEj14VmRuZBkqFbiwReogJgS1zR1n',
         u'Links': None}

        Keyword arguments:
        template -- blueprints from which to construct the new object
        kwargs -- additional named arguments
        """
        if template:
            return self._object_new.request(self._client, template, **kwargs)
        else:
            return self._object_new.request(self._client, **kwargs)

    def object_links(self, multihash, **kwargs):
        """Returns the links pointed to by the specified object.

        >> c.object_links('QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDxdXBFca7D')
        {u'Hash': u'QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDxdXBFca7D',
         u'Links': [
            {u'Hash': u'Qmd2xkBfEwEs9oMTk77A6jrsgurpF3ugXSg7dtPNFkcNMV',
             u'Name': u'Makefile', u'Size': 174},
            {u'Hash': u'QmeKozNssnkJ4NcyRidYgDY2jfRZqVEoRGfipkgath71bX',
             u'Name': u'example', u'Size': 1474},
            {u'Hash': u'QmZAL3oHMQYqsV61tGvoAVtQLs1WzRe1zkkamv9qxqnDuK',
             u'Name': u'home', u'Size': 3947},
            {u'Hash': u'QmZNPyKVriMsZwJSNXeQtVQSNU4v4KEKGUQaMT61LPahso',
             u'Name': u'lib', u'Size': 268261},
            {u'Hash': u'QmSY8RfVntt3VdxWppv9w5hWgNrE31uctgTiYwKir8eXJY',
             u'Name': u'published-version', u'Size': 55}]}

        Keyword arguments:
        multihash -- unique checksum used to identify IPFS resources
        kwargs -- additional named arguments
        """
        return self._object_links.request(self._client, multihash, **kwargs)

    def object_get(self, multihash, **kwargs):
        """Get and serialize the DAG node named by multihash.

        >> c.object_get('QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDxdXBFca7D')
        {u'Data': u'\x08\x01',
         u'Links': [
            {u'Hash': u'Qmd2xkBfEwEs9oMTk77A6jrsgurpF3ugXSg7dtPNFkcNMV',
             u'Name': u'Makefile', u'Size': 174},
            {u'Hash': u'QmeKozNssnkJ4NcyRidYgDY2jfRZqVEoRGfipkgath71bX',
             u'Name': u'example', u'Size': 1474},
            {u'Hash': u'QmZAL3oHMQYqsV61tGvoAVtQLs1WzRe1zkkamv9qxqnDuK',
            u'Name': u'home', u'Size': 3947},
            {u'Hash': u'QmZNPyKVriMsZwJSNXeQtVQSNU4v4KEKGUQaMT61LPahso',
             u'Name': u'lib', u'Size': 268261},
            {u'Hash': u'QmSY8RfVntt3VdxWppv9w5hWgNrE31uctgTiYwKir8eXJY',
             u'Name': u'published-version', u'Size': 55}]}

        Keyword arguments:
        multihash -- unique checksum used to identify IPFS resources
        kwargs -- additional named arguments
        """
        return self._object_get.request(self._client, multihash, **kwargs)

    def object_put(self, file, **kwargs):
        """Stores input as a DAG object and returns its key.

        Keyword arguments:
        file -- object from which a DAG object will be created
        kwargs -- additional named arguments
        """
        return self._object_put.request(self._client, (), file, **kwargs)

    def object_stat(self, multihash, **kwargs):
        """Get stats for the DAG node named by multihash.

        >> c.object_stat('QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDxdXBFca7D')
        {u'LinksSize': 256, u'NumLinks': 5,
         u'Hash': u'QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDxdXBFca7D',
         u'BlockSize': 258, u'CumulativeSize': 274169, u'DataSize': 2}

        Keyword arguments:
        multihash -- unique checksum used to identify IPFS resources
        kwargs -- additional named arguments
        """
        return self._object_stat.request(self._client, multihash, **kwargs)

    def object_patch(self, multihash, **kwargs):
        """Creates a new merkledag object based on an existing one.

        Keyword arguments:
        multihash -- unique checksum used to identify IPFS resources
        kwargs -- additional named arguments
        """
        return self._object_patch.request(self._client, multihash, **kwargs)

    def file_ls(self, multihash, **kwargs):
        """Lists directory contents for Unix filesystem objects.

        >> c.file_ls('QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDxdXBFca7D')
        {u'Arguments': {u'QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDxdXBFca7D':
                          u'QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDxdXBFca7D'},
         u'Objects': {
           u'QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDxdXBFca7D': {
             u'Hash': u'QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDxdXBFca7D',
             u'Links': [
               {u'Hash': u'Qmd2xkBfEwEs9oMTk77A6jrsgurpF3ugXSg7dtPNFkcNMV',
                u'Name': u'Makefile', u'Size': 163, u'Type': u'File'},
               {u'Hash': u'QmeKozNssnkJ4NcyRidYgDY2jfRZqVEoRGfipkgath71bX',
                u'Name': u'example', u'Size': 1463, u'Type': u'File'},
               {u'Hash': u'QmZAL3oHMQYqsV61tGvoAVtQLs1WzRe1zkkamv9qxqnDuK',
                u'Name': u'home', u'Size': 3947, u'Type': u'Directory'},
               {u'Hash': u'QmZNPyKVriMsZwJSNXeQtVQSNU4v4KEKGUQaMT61LPahso',
                u'Name': u'lib', u'Size': 268261, u'Type': u'Directory'},
               {u'Hash': u'QmSY8RfVntt3VdxWppv9w5hWgNrE31uctgTiYwKir8eXJY',
                u'Name': u'published-version', u'Size': 47, u'Type': u'File'}
               ],
             u'Size': 0, u'Type': u'Directory'
           }
        }}

        Keyword arguments:
        multihash -- unique checksum used to identify IPFS resources
        kwargs -- additional named arguments
        """
        return self._file_ls.request(self._client, multihash, **kwargs)

    def resolve(self, *args, **kwargs):
        """Accepts an identifier and resolves it to the referenced item.

        There are a number of mutable name protocols that can link among
        themselves and into IPNS. For example IPNS references can (currently)
        point at an IPFS object, and DNS links can point at other DNS links,
        IPNS entries, or IPFS objects. This command accepts any of these
        identifiers.

        Keyword arguments:
        args -- additional unnamed arguments
        kwargs -- additional named arguments
        """
        return self._resolve.request(self._client, *args, **kwargs)

    def name_publish(self, *args, **kwargs):
        """Publishes an object to IPNS.

        Keyword arguments:
        args -- additional unnamed arguments
        kwargs -- additional named arguments
        """
        return self._name_publish.request(self._client, *args, **kwargs)

    def name_resolve(self, *args, **kwargs):
        """Gets the value currently published at an IPNS name.

        Keyword arguments:
        args -- additional unnamed arguments
        kwargs -- additional named arguments
        """
        return self._name_resolve.request(self._client, *args, **kwargs)

    def dns(self, *args, **kwargs):
        """Resolves DNS links to the referenced object.

        Keyword arguments:
        args -- additional unnamed arguments
        kwargs -- additional named arguments
        """
        return self._dns.request(self._client, *args, **kwargs)

    def pin_add(self, *args, **kwargs):
        """Pins objects to local storage.

        Stores an IPFS object(s) from a given path locally to disk.

        Keyword arguments:
        args -- additional unnamed arguments
        kwargs -- additional named arguments
        """
        return self._pin_add.request(self._client, *args, **kwargs)

    def pin_rm(self, *args, **kwargs):
        """Removes a pinned object from local storage.

        Keyword arguments:
        args -- additional unnamed arguments
        kwargs -- additional named arguments
        """
        return self._pin_rm.request(self._client, *args, **kwargs)

    def pin_ls(self, **kwargs):
        """Lists objects pinned to local storage.

        Keyword arguments:
        kwargs -- additional named arguments
        """
        return self._pin_ls.request(self._client, **kwargs)

    def repo_gc(self, *args, **kwargs):
        """Removes stored objects that are not pinned from the repo.

        Performs a garbage collection sweep of the local set of
        stored objects and remove ones that are not pinned in order
        to reclaim hard disk space.

        Keyword arguments:
        args -- additional unnamed arguments
        kwargs -- additional named arguments
        """
        return self._repo_gc.request(self._client, *args, **kwargs)

    def id(self, *args, **kwargs):
        """Shows IPFS Node ID info.

        Returns the PublicKey, ProtocolVersion, ID, AgentVersion and
        Addresses of the connected daemon

        >> c.id()
        {u'PublicKey':
            u'CAASpgIwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwA ... BAgMBAAE=',
         u'ProtocolVersion': u'ipfs/0.1.0',
         u'ID': u'QmRA9NuuaJ2GLVgCmWewUZs79H3n4AbxnEtznazsxa1VCn',
         u'AgentVersion': u'go-ipfs/0.3.8-dev',
         u'Addresses': [
            u'/ip4/127.0.0.1/tcp/4001/ipfs/QmRA9NuuaJ2GLVgCm ... 1VCn',
            u'/ip4/192.168.1.65/tcp/4001/ipfs/QmRA9NuuaJ2GLVgCm ... 1VCn',
            u'/ip6/::1/tcp/4001/ipfs/QmRA9NuuaJ2GLVgCm ... 1VCn',
            u'/ip4/212.159.87.139/tcp/63203/ipfs/QmRA9NuuaJ2GLVgCm ... 1VCn',
            u'/ip4/212.159.87.139/tcp/63203/ipfs/QmRA9NuuaJ2GLVgCm ... 1VCn']}

        Keyword arguments:
        args -- additional unnamed arguments
        kwargs -- additional named arguments
        """
        return self._id.request(self._client, *args, **kwargs)

    def bootstrap(self, *args, **kwargs):
        """Shows peers in the bootstrap list.

        Reurns the the addresses of peers used during initial discovery of
        the IPFS network

        >> c.bootstrap()
        {u'Peers': [
            u'/ip4/104.131.131.82/tcp/4001/ipfs/QmaCpDMGvV2BGHeY ... uvuJ',
            u'/ip4/104.236.176.52/tcp/4001/ipfs/QmSoLnSGccFuZQJz ... ca9z',
            ...
            u'/ip4/104.236.151.122/tcp/4001/ipfs/QmSoLju6m7xTh3Du ... 36yx']}

        Keyword arguments:
        args -- additional unnamed arguments
        kwargs -- additional named arguments
        """
        return self._bootstrap.request(self._client, *args, **kwargs)

    def bootstrap_add(self, *args, **kwargs):
        """Adds peers to the bootstrap list.

        Keyword arguments:
        args -- additional unnamed arguments
        kwargs -- additional named arguments
        """
        return self._bootstrap_add.request(self._client, *args, **kwargs)

    def bootstrap_rm(self, *args, **kwargs):
        """Removes peers from the bootstrap list.

        Keyword arguments:
        args -- additional unnamed arguments
        kwargs -- additional named arguments
        """
        return self._bootstrap_rm.request(self._client, *args, **kwargs)

    def swarm_peers(self, *args, **kwargs):
        """Returns the addresses & IDs of currently connected peers.

        >> c.swarm_peers()
        {u'Strings': [
            u'/ip4/104.155.70.200/tcp/4001/ipfs/QmTnvDqXnvrcwyVY7 ... 1fNr',
            u'/ip4/108.54.113.161/tcp/32899/ipfs/QmbBHw1Xx9pUpAbrV ... gGtC',
            ...
            u'/ip4/92.1.172.181/tcp/4001/ipfs/QmdPe9Xs5YGCoVN8nk ... 5cKD',
            u'/ip4/94.242.232.165/tcp/4001/ipfs/QmUdVdJs3dM6Qi6Tf ... Dgx9']}

        Keyword arguments:
        args -- additional unnamed arguments
        kwargs -- additional named arguments
        """
        return self._swarm_peers.request(self._client, *args, **kwargs)

    def swarm_addrs(self, *args, **kwargs):
        """Returns the addresses of currently connected peers by peer id.

        >> pprint(c.swarm_addrs())
        {u'Addrs': {
            u'QmNd92Ndyccns8vTvdK66H1PC4qRXzKz3ewAqAzLbooEpB':
                [u'/ip4/127.0.0.1/tcp/4002', u'/ip4/192.168.0.6/tcp/4002',
                 u'/ip4/24.155.157.5/tcp/4002'],
            u'QmNeK3hRF5Pu9dPcMDKXvYofQioskuGfQZEQz43UDkLepK':
                [u'/ip4/127.0.0.1/tcp/4001', u'/ip4/178.62.206.163/tcp/4001'],
            ...
        }}

        Keyword arguments:
        args -- additional unnamed arguments
        kwargs -- additional named arguments
        """
        return self._swarm_addrs.request(self._client, *args, **kwargs)

    def swarm_connect(self, *args, **kwargs):
        """Opens a connection to a given address.

        Keyword arguments:
        args -- additional unnamed arguments
        kwargs -- additional named arguments
        """
        return self._swarm_connecti.request(self._client, *args, **kwargs)

    def swarm_disconnect(self, *args, **kwargs):
        """Closes the connection to a given address.

        Keyword arguments:
        args -- additional unnamed arguments
        kwargs -- additional named arguments
        """
        return self._swarm_disconnect.request(self._client, *args, **kwargs)

    def swarm_filters_add(self, *args, **kwargs):
        """Adds a given multiaddr filter to the filter list.

        Keyword arguments:
        args -- additional unnamed arguments
        kwargs -- additional named arguments
        """
        return self._swarm_filters_add.request(self._client, *args, **kwargs)

    def swarm_filters_rm(self, *args, **kwargs):
        """Removes a given multiaddr filter from the filter list.

        Keyword arguments:
        args -- additional unnamed arguments
        kwargs -- additional named arguments
        """
        return self._swarm_filters_rm.request(self._client, *args, **kwargs)

    def dht_query(self, *args, **kwargs):
        """Finds the closest Peer IDs to a given Peer ID by querying the DHT.

        Keyword arguments:
        args -- additional unnamed arguments
        kwargs -- additional named arguments
        """
        return self._dht_query.request(self._client, *args, **kwargs)

    def dht_findprovs(self, *args, **kwargs):
        """Finds peers in the DHT that can provide an exact value, given a key.

        Keyword arguments:
        args -- additional unnamed arguments
        kwargs -- additional named arguments
        """
        return self._dht_findprovs.request(self._client, *args, **kwargs)

    def dht_findpeer(self, *args, **kwargs):
        """Queries the DHT for all of the associated multiaddresses.

        Keyword arguments:
        args -- additional unnamed arguments
        kwargs -- additional named arguments
        """
        return self._dht_findpeer.request(self._client, *args, **kwargs)

    def dht_get(self, *args, **kwargs):
        """Queries the DHT for its best value related to given key.

        Keyword arguments:
        args -- additional unnamed arguments
        kwargs -- additional named arguments
        """
        res = self._dht_get.request(self._client, *args, **kwargs)
        if isinstance(res, dict) and "Extra" in res:
            return res["Extra"]
        else:
            for r in res:
                if "Extra" in r and len(r["Extra"]) > 0:
                    return r["Extra"]
        raise ipfsApiError("empty response from DHT")

    def dht_put(self, key, value, **kwargs):
        """Writes a key/value pair to the DHT.

        Keyword arguments:
        key -- a unique identifier
        value -- object to be associated with the given key
        kwargs -- additional named arguments
        """
        return self._dht_put.request(self._client, key, value, **kwargs)

    def ping(self, *args, **kwargs):
        """Provides round-trip latency information for the routing system.

        Finds nodes via the routing system, sends pings, waits for pongs,
        and prints out round-trip latency information.

        Keyword arguments:
        args -- additional unnamed arguments
        kwargs -- additional named arguments
        """
        return self._ping.request(self._client, *args, **kwargs)

    def config(self, *args, **kwargs):
        """Controls configuration variables.

        Keyword arguments:
        args -- additional unnamed arguments
        kwargs -- additional named arguments
        """
        return self._config.request(self._client, *args, **kwargs)

    def config_show(self, *args, **kwargs):
        """Returns a dict containing the server's configuration.

        >> config = ipfs_client.config_show()
        >> pprint(config['Addresses']
        {u'API': u'/ip4/127.0.0.1/tcp/5001',
         u'Gateway': u'/ip4/127.0.0.1/tcp/8080',
         u'Swarm': [u'/ip4/0.0.0.0/tcp/4001', u'/ip6/::/tcp/4001']},
        >> pprint(config['Discovery'])
        {u'MDNS': {u'Enabled': True, u'Interval': 10}}

        Keyword arguments:
        args -- additional unnamed arguments
        kwargs -- additional named arguments
        """
        return self._config_show.request(self._client, *args, **kwargs)

    def config_replace(self, *args, **kwargs):
        """Replaces the existing config with a user-defined config.

        Make sure to back up the config file first if neccessary, as this
        operation can't be undone.

        Keyword arguments:
        args -- additional unnamed arguments
        kwargs -- additional named arguments
        """
        return self._config_replace.request(self._client, *args, **kwargs)

    def version(self, **kwargs):
        """Returns the software version of the currently connected node.

        >> c.version() # doctest: +ELLIPSIS
        {u'Version': u'0.3...'}

        Keyword arguments:
        kwargs -- additional named arguments
        """
        return self._version.request(self._client, **kwargs)

    def files_cp(self, source, dest, **kwargs):
        """Copies files into MFS.

        Keyword arguments:
        source -- file to be copied
        dest -- destination to which the file will be copied
        kwargs -- additional named arguments
        """
        return self._files_cp.request(self._client, source, dest, **kwargs)

    def files_ls(self, path, **kwargs):
        """Lists directory contents in MFS.

        Keyword arguments:
        path -- filepath within the MFS
        kwargs -- additional named arguments
        """
        return self._files_ls.request(self._client, path, **kwargs)

    def files_mkdir(self, path, **kwargs):
        """Creates a directory in MFS.

        Keyword arguments:
        path -- filepath within the MFS
        kwargs -- additional named arguments
        """
        return self._files_mkdir.request(self._client, path, **kwargs)

    def files_stat(self, path, **kwargs):
        """Displays a file's status (including it's hash) in MFS.

        Keyword arguments:
        path -- filepath within the MFS
        kwargs -- additional named arguments
        """
        return self._files_stat.request(self._client, path, **kwargs)

    def files_rm(self, path, **kwargs):
        """Removes a file from MFS.

        Keyword arguments:
        path -- filepath within the MFS
        kwargs -- additional named arguments
        """
        return self._files_rm.request(self._client, path, **kwargs)

    def files_read(self, path, **kwargs):
        """Reads a file stored in MFS.

        Keyword arguments:
        path -- filepath within the MFS
        kwargs -- additional named arguments
        """
        return self._files_read.request(self._client, path, **kwargs)

    def files_write(self, path, file, **kwargs):
        """Writes to a mutable file in MFS.

        Keyword arguments:
        path -- filepath within the MFS
        file -- object to be written
        kwargs -- additional named arguments
        """
        return self._files_write.request(self._client, (path,), file, **kwargs)

    def files_mv(self, source, dest, **kwargs):
        """Moves MFS files.

        Keyword arguments:
        source -- existing filepath within the MFS
        dest -- destination to which the file will be moved in the MFS
        kwargs -- additional named arguments
        """
        return self._files_mv.request(self._client, source, dest, **kwargs)

    ###########
    # HELPERS #
    ###########

    @utils.return_field('Hash')
    def add_str(self, string, **kwargs):
        """Adds a Python string as a file to IPFS.

        >> ipfs_client.add_str('Mary had a little lamb')
        u'QmZfF6C9j4VtoCsTp4KSrhYH47QMd3DNXVZBKaxJdhaPab'

        Also accepts and will stream generator objects.

        Keyword arguments:
        string -- content to be added as a file
        kwargs -- additional named arguments
        """
        chunk_size = kwargs.pop('chunk_size',
                                multipart.default_chunk_size)
        body, headers = multipart.stream_text(string,
                                              chunk_size=chunk_size)
        return self._client.request('/add', data=body,
                                    headers=headers, **kwargs)

    def add_json(self, json_obj, **kwargs):
        """Adds a json-serializable Python dict as a json file to IPFS.

        >> ipfs_client.add_json({'one': 1, 'two': 2, 'three': 3})
        u'QmVz9g7m5u3oHiNKHj2CJX1dbG1gtismRS3g9NaPBBLbob'

        Keyword arguments:
        string -- a json-serializable Python dict
        kwargs -- additional named arguments
        """
        return self.add_str(utils.encode_json(json_obj), **kwargs)

    def get_json(self, multihash, **kwargs):
        """Loads a json object from IPFS.

        >> c.get_json('QmVz9g7m5u3oHiNKHj2CJX1dbG1gtismRS3g9NaPBBLbob')
        {u'one': 1, u'two': 2, u'three': 3}

        Keyword arguments:
        multihash -- unique checksum used to identify IPFS resources
        kwargs -- additional named arguments
        """
        return self.cat(multihash, decoder='json', **kwargs)

    def add_pyobj(self, py_obj, **kwargs):
        """Adds a picklable Python object as a file to IPFS.

        >> c.add_pyobj([0, 1.0, 2j, '3', 4e5])
        u'QmdCWFLDXqgdWQY9kVubbEHBbkieKd3uo7MtCm7nTZZE9K'

        Keyword arguments:
        string -- a picklable Python object
        kwargs -- additional named arguments
        """
        return self.add_str(utils.encode_pyobj(py_obj), **kwargs)

    def get_pyobj(self, multihash, **kwargs):
        """Loads a pickled Python object from IPFS.

        >> c.get_pyobj('QmdCWFLDXqgdWQY9kVubbEHBbkieKd3uo7MtCm7nTZZE9K')
        [0, 1.0, 2j, '3', 400000.0]

        Keyword arguments:
        multihash -- unique checksum used to identify IPFS resources
        kwargs -- additional named arguments
        """
        return utils.parse_pyobj(self.cat(multihash, **kwargs))
