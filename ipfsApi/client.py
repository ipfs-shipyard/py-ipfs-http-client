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

    _clientfactory = http.HTTPClient

    def __init__(self,
                 host=None,
                 port=None,
                 base=None,
                 default_enc='json',
                 **defaults):

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
        """
        return req(file, recursive=recursive, **kwargs)

    @ArgCommand('/cat')
    def cat(req, multihash, **kwargs):
        """
        """
        return req(multihash, **kwargs)

    @ArgCommand('/ls')
    def ls(req, multihash, **kwargs):
        """
        """
        return req(multihash, **kwargs)

    @ArgCommand('/refs')
    def refs(req, multihash, **kwargs):
        """
        """
        return req(multihash, **kwargs)

    # DATA STRUCTURE COMMANDS

    @ArgCommand('/block/stat')
    def block_stat(req, multihash, **kwargs):
        """
        """
        return req(multihash, **kwargs)

    @ArgCommand('/block/get')
    def block_get(req, multihash, **kwargs):
        """
        """
        return req(multihash, **kwargs)

    @FileCommand('/block/put', accept_multiple=False)
    def block_put(req, file, **kwargs):
        """
        """
        return req(file, **kwargs)

    @ArgCommand('/object/data')
    def object_data(req, multihash, **kwargs):
        """
        """
        return req(multihash, **kwargs)

    @ArgCommand('/object/links')
    def object_links(req, multihash, **kwargs):
        """
        """
        return req(multihash, **kwargs)

    @ArgCommand('/object/get')
    def object_get(req, multihash, **kwargs):
        """
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
        """
        return req(*args, **kwargs)

    @Command('/bootstrap')
    def bootstrap(req, *args, **kwargs):
        """
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
        """
        return req(*args, **kwargs)

    @Command('/swarm/addrs')
    def swarm_addrs(req, *args, **kwargs):
        """
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
        """
        return req(**kwargs)

    ###########
    # HELPERS #
    ###########

    @utils.return_field('Hash')
    def add_str(self, string, **kwargs):
        """
        Adds a Python string as a file to IPFS.
        """
        return self.add(utils.make_string_buffer(string), **kwargs)

    @utils.return_field('Hash')
    def add_json(self, json_obj, **kwargs):
        """
        Adds a json-serializable Python dict as a json file to IPFS.
        """
        return self.add(utils.make_json_buffer(json_obj), **kwargs)

    def get_json(self, multihash, **kwargs):
        """
        Loads a json object from IPFS.
        """
        return self.cat(multihash, decoder='json', **kwargs)

    @utils.return_field('Hash')
    def add_pyobj(self, py_obj, **kwargs):
        """
        Adds a picklable Python object as a file to IPFS.
        """
        return self.add(utils.make_pyobj_buffer(py_obj), **kwargs)

    def get_pyobj(self, multihash, **kwargs):
        """
        Loads a pickled Python object from IPFS.
        """
        return utils.parse_pyobj(self.cat(multihash, **kwargs))
