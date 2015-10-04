"""
IPFS API Bindings for Python
"""
from __future__ import absolute_import

from . import http
from . import utils
from .commands import Command, ArgCommand, FileCommand

default_host = 'localhost'
default_port = 5001
default_base = 'api/v0'


class Client(object):
    """
    A TCP client for interacting with an IPFS daemon
    """

    _clientfactory = http.HTTPClient

    def __init__(self,
                 host=None,
                 port=None,
                 base=None,
                 default_enc='json',
                 **defaults):

        """
        Connect to the API port of an IPFS node
        """
        if host is None:
            host = default_host
        if port is None:
            port = default_port
        if base is None:
            base = default_base

        self._client = self._clientfactory(host, port, base,
                                           default_enc, **defaults)

    # BASIC COMMANDS

    @FileCommand('/add')
    def add(req, file, recursive=False, **kwargs):
        """
        Add a file, or directory of files to IPFS

        >> with io.open('nurseryrhyme.txt', 'w', encoding='utf-8') as f:
        ...     numbytes = f.write(u'Mary had a little lamb')
        >> c.add('nurseryrhyme.txt')
        {u'Hash': u'QmZfF6C9j4VtoCsTp4KSrhYH47QMd3DNXVZBKaxJdhaPab',
         u'Name': u'nurseryrhyme.txt'}
        """
        return req(file, recursive=recursive, **kwargs)

    @ArgCommand('/cat')
    def cat(req, multihash, **kwargs):
        r"""
        Returns the contents of a file identified by hash, as a string

        >> c.cat('QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDxdXBFca7D')
        Traceback (most recent call last):
          ...
        ipfsApiError: this dag node is a directory
        >> c.cat('QmeKozNssnkJ4NcyRidYgDY2jfRZqVEoRGfipkgath71bX')[:60]
        u'<!DOCTYPE html>\n<html>\n\n<head>\n<title>ipfs example viewer</t'
        """
        return req(multihash, **kwargs)

    @ArgCommand('/ls')
    def ls(req, multihash, **kwargs):
        """
        Returns a list of objects linked to the given hash

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
        """
        return req(multihash, **kwargs)

    @ArgCommand('/refs')
    def refs(req, multihash, **kwargs):
        """
        Returns a list of hashes of objects referenced to the given hash

        >> c.refs('QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDxdXBFca7D')
        [{u'Ref': u'Qmd2xkBfEwEs9oMTk77A6jrsgurpF3ugXSg7dtPNFkcNMV',
          u'Err': u''},
         ...
         {u'Ref': u'QmSY8RfVntt3VdxWppv9w5hWgNrE31uctgTiYwKir8eXJY',
         u'Err': u''}]
        """
        return req(multihash, **kwargs)

    # DATA STRUCTURE COMMANDS

    @ArgCommand('/block/stat')
    def block_stat(req, multihash, **kwargs):
        """
        Returns a dict with the size of the block with the given hash

        >> c.block_stat('QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDxdXBFca7D')
        {u'Key': u'QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDxdXBFca7D',
         u'Size': 258}
        """
        return req(multihash, **kwargs)

    @ArgCommand('/block/get')
    def block_get(req, multihash, **kwargs):
        r"""
        Returns the raw contents of a block

        >> c.block_get('QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDxdXBFca7D')
        u'\x121\n"\x12 \xdaW> ... \x11published-version\x187\n\x02\x08\x01'
        """
        return req(multihash, **kwargs)

    @FileCommand('/block/put', accept_multiple=False)
    def block_put(req, file, **kwargs):
        """
        >> c.block_put(io.StringIO(u'Mary had a little lamb'))
        {u'Key': u'QmeV6C6XVt1wf7V7as7Yak3mxPma8jzpqyhtRtCvpKcfBb',
         u'Size': 22}
        """
        return req(file, **kwargs)

    @ArgCommand('/object/data')
    def object_data(req, multihash, **kwargs):
        r"""
        >> c.object_data('QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDxdXBFca7D')
        u'\x08\x01'
        """
        return req(multihash, **kwargs)

    @ArgCommand('/object/new')
    def object_new(req, template=None, **kwargs):
        """
        >> c.object_new()
        {u'Hash': u'QmdfTbBqBPQ7VNxZEYEj14VmRuZBkqFbiwReogJgS1zR1n',
         u'Links': None}
        """
        if template:
            return req(template, **kwargs)
        else:
            return req(**kwargs)

    @ArgCommand('/object/links')
    def object_links(req, multihash, **kwargs):
        """
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
        """
        return req(multihash, **kwargs)

    @ArgCommand('/object/get')
    def object_get(req, multihash, **kwargs):
        """
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
        """
        return req(multihash, **kwargs)

    @FileCommand('/object/put')
    def object_put(req, file, **kwargs):
        """
        """
        return req(file, **kwargs)

    @ArgCommand('/object/stat')
    def object_stat(req, multihash, **kwargs):
        """
        >> c.object_stat('QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDxdXBFca7D')
        {u'LinksSize': 256, u'NumLinks': 5,
         u'Hash': u'QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDxdXBFca7D',
         u'BlockSize': 258, u'CumulativeSize': 274169, u'DataSize': 2}
        """
        return req(multihash, **kwargs)

    @ArgCommand('/object/patch')
    def object_patch(req, multihash, **kwargs):
        """
        """
        return req(multihash, **kwargs)

    @ArgCommand('/file/ls')
    def file_ls(req, multihash, **kwargs):
        """
        List file and directory objects in the object identified by a hash

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
        """
        return req(multihash, **kwargs)

    # ADVANCED COMMANDS

    @ArgCommand('/resolve')
    def resolve(req, *args, **kwargs):
        """
        """
        return req(*args, **kwargs)

    @ArgCommand('/name/publish')
    def name_publish(req, *args, **kwargs):
        """
        """
        return req(*args, **kwargs)

    @ArgCommand('/name/resolve')
    def name_resolve(req, *args, **kwargs):
        """
        """
        return req(*args, **kwargs)

    @ArgCommand('/dns')
    def dns(req, *args, **kwargs):
        """
        """
        return req(*args, **kwargs)

    @ArgCommand('/pin/add')
    def pin_add(req, *args, **kwargs):
        """
        """
        return req(*args, **kwargs)

    @ArgCommand('/pin/rm')
    def pin_rm(req, *args, **kwargs):
        """
        """
        return req(*args, **kwargs)

    @Command('/pin/ls')
    def pin_ls(req, **kwargs):
        """
        """
        return req(**kwargs)

    @Command('/repo/gc')
    def repo_gc(req, *args, **kwargs):
        """
        """
        return req(*args, **kwargs)

    # NETWORK COMMANDS

    @Command('/id')
    def id(req, *args, **kwargs):
        """
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
        """
        return req(*args, **kwargs)

    @Command('/bootstrap')
    def bootstrap(req, *args, **kwargs):
        """
        Reurns the the addresses of peers used during initial discovery of
        the IPFS network

        >> c.bootstrap()
        {u'Peers': [
            u'/ip4/104.131.131.82/tcp/4001/ipfs/QmaCpDMGvV2BGHeY ... uvuJ',
            u'/ip4/104.236.176.52/tcp/4001/ipfs/QmSoLnSGccFuZQJz ... ca9z',
            ...
            u'/ip4/104.236.151.122/tcp/4001/ipfs/QmSoLju6m7xTh3Du ... 36yx']}
        """
        return req(*args, **kwargs)

    @ArgCommand('/bootstrap/add')
    def bootstrap_add(req, *args, **kwargs):
        """
        """
        return req(*args, **kwargs)

    @ArgCommand('/bootstrap/rm')
    def bootstrap_rm(req, *args, **kwargs):
        """
        """
        return req(*args, **kwargs)

    @Command('/swarm/peers')
    def swarm_peers(req, *args, **kwargs):
        """
        Returns the addresses & IDs of currently connected peers

        >> c.swarm_peers()
        {u'Strings': [
            u'/ip4/104.155.70.200/tcp/4001/ipfs/QmTnvDqXnvrcwyVY7 ... 1fNr',
            u'/ip4/108.54.113.161/tcp/32899/ipfs/QmbBHw1Xx9pUpAbrV ... gGtC',
            ...
            u'/ip4/92.1.172.181/tcp/4001/ipfs/QmdPe9Xs5YGCoVN8nk ... 5cKD',
            u'/ip4/94.242.232.165/tcp/4001/ipfs/QmUdVdJs3dM6Qi6Tf ... Dgx9']}
        """
        return req(*args, **kwargs)

    @Command('/swarm/addrs')
    def swarm_addrs(req, *args, **kwargs):
        """
        Returns the addresses of currently connected peers by peer id
        >> pprint(c.swarm_addrs())
        {u'Addrs': {
            u'QmNd92Ndyccns8vTvdK66H1PC4qRXzKz3ewAqAzLbooEpB':
                [u'/ip4/127.0.0.1/tcp/4002', u'/ip4/192.168.0.6/tcp/4002',
                 u'/ip4/24.155.157.5/tcp/4002'],
            u'QmNeK3hRF5Pu9dPcMDKXvYofQioskuGfQZEQz43UDkLepK':
                [u'/ip4/127.0.0.1/tcp/4001', u'/ip4/178.62.206.163/tcp/4001'],
            ...
        }}
        """
        return req(*args, **kwargs)

    @ArgCommand('/swarm/connect')
    def swarm_connect(req, *args, **kwargs):
        """
        """
        return req(*args, **kwargs)

    @ArgCommand('/swarm/disconnect')
    def swarm_disconnect(req, *args, **kwargs):
        """
        """
        return req(*args, **kwargs)

    @ArgCommand('/swarm/filters/add')
    def swarm_filters_add(req, *args, **kwargs):
        """
        """
        return req(*args, **kwargs)

    @ArgCommand('/swarm/filters/rm')
    def swarm_filters_rm(req, *args, **kwargs):
        """
        """
        return req(*args, **kwargs)

    @ArgCommand('/dht/query')
    def dht_query(req, *args, **kwargs):
        """
        """
        return req(*args, **kwargs)

    @ArgCommand('/dht/findprovs')
    def dht_findprovs(req, *args, **kwargs):
        """
        """
        return req(*args, **kwargs)

    @ArgCommand('/dht/findpeer')
    def dht_findpeer(req, *args, **kwargs):
        """
        """
        return req(*args, **kwargs)

    @utils.return_field('Extra')
    @ArgCommand('/dht/get')
    def dht_get(req, *args, **kwargs):
        """
        """
        return req(*args, **kwargs)

    @ArgCommand('/dht/put', argc=2)
    def dht_put(req, key, value, **kwargs):
        """
        """
        return req(key, value, **kwargs)

    @ArgCommand('/ping')
    def ping(req, *args, **kwargs):
        """
        """
        return req(*args, **kwargs)

    # TOOL COMMANDS

    @ArgCommand('/config')
    def config(req, *args, **kwargs):
        """
        """
        return req(*args, **kwargs)

    @Command('/config/show')
    def config_show(req, *args, **kwargs):
        """
        Returns a dict containing the server's configuration

        >> config = ipfs_client.config_show()
        >> pprint(config['Addresses']
        {u'API': u'/ip4/127.0.0.1/tcp/5001',
         u'Gateway': u'/ip4/127.0.0.1/tcp/8080',
         u'Swarm': [u'/ip4/0.0.0.0/tcp/4001', u'/ip6/::/tcp/4001']},
        >> pprint(config['Discovery'])
        {u'MDNS': {u'Enabled': True, u'Interval': 10}}
        """
        return req(*args, **kwargs)

    @ArgCommand('/config/replace')
    def config_replace(req, *args, **kwargs):
        """
        """
        return req(*args, **kwargs)

    @Command('/version')
    def version(req, **kwargs):
        """
        Returns the software version of the currently connected node

        >> c.version() # doctest: +ELLIPSIS
        {u'Version': u'0.3...'}
        """
        return req(**kwargs)

    ###########
    # HELPERS #
    ###########

    @utils.return_field('Hash')
    def add_str(self, string, **kwargs):
        """
        Adds a Python string as a file to IPFS.

        >> ipfs_client.add_str('Mary had a little lamb')
        u'QmZfF6C9j4VtoCsTp4KSrhYH47QMd3DNXVZBKaxJdhaPab'
        """
        return self.add(utils.make_string_buffer(string), **kwargs)

    @utils.return_field('Hash')
    def add_json(self, json_obj, **kwargs):
        """
        Adds a json-serializable Python dict as a json file to IPFS.

        >> ipfs_client.add_json({'one': 1, 'two': 2, 'three': 3})
        u'QmVz9g7m5u3oHiNKHj2CJX1dbG1gtismRS3g9NaPBBLbob'
        """
        return self.add(utils.make_json_buffer(json_obj), **kwargs)

    def get_json(self, multihash, **kwargs):
        """
        Loads a json object from IPFS.

        >> c.get_json('QmVz9g7m5u3oHiNKHj2CJX1dbG1gtismRS3g9NaPBBLbob')
        {u'one': 1, u'two': 2, u'three': 3}
        """
        return self.cat(multihash, decoder='json', **kwargs)

    @utils.return_field('Hash')
    def add_pyobj(self, py_obj, **kwargs):
        """
        Adds a picklable Python object as a file to IPFS.

        >> c.add_pyobj([0, 1.0, 2j, '3', 4e5])
        u'QmdCWFLDXqgdWQY9kVubbEHBbkieKd3uo7MtCm7nTZZE9K'
        """
        return self.add(utils.make_pyobj_buffer(py_obj), **kwargs)

    def get_pyobj(self, multihash, **kwargs):
        """
        Loads a pickled Python object from IPFS.

        >> c.get_pyobj('QmdCWFLDXqgdWQY9kVubbEHBbkieKd3uo7MtCm7nTZZE9K')
        [0, 1.0, 2j, '3', 400000.0]
        """
        return utils.parse_pyobj(self.cat(multihash, **kwargs))
