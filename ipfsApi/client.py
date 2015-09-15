"""
IPFS API Bindings for Python
"""
from __future__ import absolute_import

from . import http
from . import utils
from .commands import Command, ArgCommand, FileCommand
from .exceptions import InvalidCommand

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

        self._client = self._clientfactory(host, port, base, default_enc)

        # default request keyword-args
        if 'opts' in defaults:
            defaults['opts'].update({'encoding': default_enc})
        else:
            defaults.update({'opts': {'encoding': default_enc}})

        self._defaults = defaults

    # BASIC COMMANDS
    def add(self, *args, **kwargs):
     """  """
     FileCommand('/add').request(self, **kwargs)

    def cat(self,*args,**kwargs):
     """  """
        ArgCommand('/cat').request(self, **kwargs)
        
    def ls(self,*args,**kwargs):
     """  """
        ArgCommand('/ls').request(self, **kwargs)

    def refs(self,*args,**kwargs):
     """  """
        ArgCommand('/refs').request(self, **kwargs)

    # DATA STRUCTURE COMMANDS
    def block_stat(self,*args,**kwargs):
     """  """
        ArgCommand('/block/stat').request(self, **kwargs)

    def block_get(self,*args,**kwargs):
     """  """
        ArgCommand('/block/get').request(self, **kwargs)

    def block_put(self,*args,**kwargs):
     """  """
     FileCommand('/block/put', accept_multiple=False).request(self, **kwargs)
    def object_data(self,*args,**kwargs):
     """  """
        ArgCommand('/object/data').request(self, **kwargs)
    def object_links(self,*args,**kwargs):
     """  """
        ArgCommand('/object/links').request(self, **kwargs)
    def object_get(self,*args,**kwargs):
     """  """
        ArgCommand('/object/get').request(self, **kwargs)
    def object_put(self,*args,**kwargs):
     """  """
     FileCommand('/object/put').request(self, **kwargs)
    def object_stat(self,*args,**kwargs):
     """  """
        ArgCommand('/object/stat').request(self, **kwargs)
    def object_patch(self,*args,**kwargs):
     """  """
        ArgCommand('/object/patch').request(self, **kwargs)
    def file_ls(self,*args,**kwargs):
     """  """
        ArgCommand('/file/ls').request(self, **kwargs)

    # ADVANCED COMMANDS
    def resolve(self,*args,**kwargs):
     """  """
        ArgCommand('/resolve').request(self, **kwargs)
    def name_publish(self,*args,**kwargs):
     """  """
        ArgCommand('/name/publish').request(self, **kwargs)
    def name_resolve(self,*args,**kwargs):
     """  """
        ArgCommand('/name/resolve').request(self, **kwargs)
    def dns(self,*args,**kwargs):
     """  """
        ArgCommand('/dns').request(self, **kwargs)
    def pin_add(self,*args,**kwargs):
     """  """
        ArgCommand('/pin/add').request(self, **kwargs)
    def pin_rm(self,*args,**kwargs):
     """  """
        ArgCommand('/pin/rm').request(self, **kwargs)
    def pin_ls(self,*args,**kwargs):
     """  """
         Command('/pin/ls').request(self, **kwargs)
    def repo_gc(self,*args,**kwargs):
     """  """
         Command('/repo/gc').request(self, **kwargs)

    # NETWORK COMMANDS
    def id(self,*args,**kwargs):
     """  """
         Command('/id').request(self, **kwargs)
    def bootstrap(self,*args,**kwargs):
     """  """
         Command('/bootstrap').request(self, **kwargs)
    def bootstrap_add(self,*args,**kwargs):
     """  """
        ArgCommand('/bootstrap/add').request(self, **kwargs)
    def bootstrap_rm(self,*args,**kwargs):
     """  """
        ArgCommand('/bootstrap/rm').request(self, **kwargs)
    def swarm_peers(self,*args,**kwargs):
     """  """
         Command('/swarm/peers').request(self, **kwargs)
    def swarm_addrs(self,*args,**kwargs):
     """  """
         Command('/swarm/addrs').request(self, **kwargs)
    def swarm_connect(self,*args,**kwargs):
     """  """
        ArgCommand('/swarm/connect').request(self, **kwargs)
    def swarm_disconnect(self,*args,**kwargs):
     """  """
        ArgCommand('/swarm/disconnect').request(self, **kwargs)
    def swarm_filters_add(self,*args,**kwargs):
     """  """
        ArgCommand('/swarm/filters/add').request(self, **kwargs)
    def swarm_filters_rm(self,*args,**kwargs):
     """  """
        ArgCommand('/swarm/filters/rm').request(self, **kwargs)
    def dht_query(self,*args,**kwargs):
     """  """
        ArgCommand('/dht/query').request(self, **kwargs)
    def dht_findprovs(self,*args,**kwargs):
     """  """
        ArgCommand('/dht/findprovs').request(self, **kwargs)
    def dht_findpeer(self,*args,**kwargs):
     """  """
        ArgCommand('/dht/findpeer').request(self, **kwargs)
    def dht_get(self,*args,**kwargs):
     """  """
        ArgCommand('/dht/get', decoder='json', post_hook=lambda r: r[u"Extra"]).request(self, **kwargs)
    def dht_put(self,*args,**kwargs):
     """  """
        ArgCommand('/dht/put', argc=2).request(self, **kwargs)
    def ping(self,*args,**kwargs):
     """  """
        ArgCommand('/ping').request(self, **kwargs)

    # TOOL COMMANDS
    def config(self,*args,**kwargs):
     """  """
        ArgCommand('/config').request(self, **kwargs)
    def config_show(self,*args,**kwargs):
     """  """
         Command('/config/show').request(self, **kwargs)
    def config_replace(self,*args,**kwargs):
     """  """
        ArgCommand('/config/replace').request(self, **kwargs)
    def version(self,*args,**kwargs):
     """  """
         Command('/version')

    def __getattribute__(self, name):
        """
        Prepares command request or raises InvalidCommand exception.
        """
        try:
            attr = object.__getattribute__(self, name)
            if isinstance(attr, Command):
                return attr.prepare(self._client, **self._defaults)
            else:
                return attr
        except AttributeError:
            # all non-private attributes are api commands
            if name[0] != '_':
                raise InvalidCommand
            else:
                raise AttributeError

    ###########
    # HELPERS #
    ###########

    def add_str(self, string, **kwargs):
        """Adds a Python string as a file to IPFS."""
        res = self.add(utils.make_string_buffer(string), **kwargs)
        try:
            return res['Hash']
        except:
            return res

    def add_json(self, json_obj, **kwargs):
        """Adds a json-serializable Python dict as a json file to IPFS."""
        res = self.add(utils.make_json_buffer(json_obj), **kwargs)
        try:
            return res['Hash']
        except:
            return res

    def get_json(self, multihash, **kwargs):
        """Loads a json object from IPFS."""
        return self.cat(multihash, decoder='json', **kwargs)

    def add_pyobj(self, py_obj, **kwargs):
        """Adds a picklable Python object as a file to IPFS."""
        res = self.add(utils.make_pyobj_buffer(py_obj), **kwargs)
        try:
            return res['Hash']
        except:
            return res

    def get_pyobj(self, multihash, **kwargs):
        """Loads a pickled Python object from IPFS."""
        return utils.parse_pyobj(self.cat(multihash, **kwargs))
