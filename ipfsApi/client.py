"""
IPFS API Bindings for Python
"""
from . import http
from . import utils
from .commands import Command, \
                      ArgCommand, \
                      FileCommand
from .exceptions import InvalidCommand

default_host = 'localhost'
default_port = 5001
default_base = 'api/v0'


class Client(object):

    __client__ = http.HTTPClient


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
        
        self._client = self.__client__(host, port, base, default_enc)
        
        # default request keyword-args
        if defaults.has_key('opts'):
            defaults['opts'].update({'encoding': default_enc})
        else:
            defaults.update({'opts': {'encoding': default_enc}})

        self._defaults = defaults


        ############
        # COMMANDS #
        ############
        
        # BASIC COMMANDS
        self.add                = FileCommand('/add')
        self.cat                =  ArgCommand('/cat')
        self.ls                 =  ArgCommand('/ls')
        self.refs               =  ArgCommand('/refs')
        
        # DATA STRUCTURE COMMANDS
        self.block_stat         =  ArgCommand('/block/stat')
        self.block_get          =  ArgCommand('/block/get')
        self.block_put          = FileCommand('/block/put',
                                              accept_multiple=False)
        self.object_data        =  ArgCommand('/object/data')
        self.object_links       =  ArgCommand('/object/links')
        self.object_get         =  ArgCommand('/object/get')
        self.object_put         = FileCommand('/object/put')
        self.object_stat        =  ArgCommand('/object/stat')
        self.object_patch       =  ArgCommand('/object/patch')
        self.file_ls            =  ArgCommand('/file/ls')

        # ADVANCED COMMANDS
        self.resolve            =  ArgCommand('/resolve')
        self.name_publish       =  ArgCommand('/name/publish')
        self.name_resolve       =  ArgCommand('/name/resolve')
        self.dns                =  ArgCommand('/dns')
        self.pin_add            =  ArgCommand('/pin/add')
        self.pin_rm             =  ArgCommand('/pin/rm')
        self.pin_ls             =     Command('/pin/ls')
        self.repo_gc            =     Command('/repo/gc')

        # NETWORK COMMANDS
        self.id                 =     Command('/id')
        self.bootstrap          =     Command('/bootstrap')
        self.swarm_peers        =     Command('/swarm/peers')
        self.swarm_addrs        =     Command('/swarm/addrs')
        self.swarm_connect      =  ArgCommand('/swarm/connect')
        self.swarm_disconnect   =  ArgCommand('/swarm/disconnect')
        self.swarm_filters_add  =  ArgCommand('/swarm/filters/add')
        self.swarm_filters_rm   =  ArgCommand('/swarm/filters/rm')
        self.dht_query          =  ArgCommand('/dht/query')
        self.dht_findprovs      =  ArgCommand('/dht/findprovs')
        self.dht_findpeer       =  ArgCommand('/dht/findpeer')
        self.dht_get            =  ArgCommand('/dht/get',
                                              decoder='json',
                                              post_hook=lambda r: r[u"Extra"])
        self.dht_put            =  ArgCommand('/dht/put', argc=2)
        self.ping               =  ArgCommand('/ping')
        
        # TOOL COMMANDS
        self.config             =  ArgCommand('/config')
        self.config_show        =     Command('/config/show')
        self.config_replace     =  ArgCommand('/config/replace')
        self.version            =     Command('/version')


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
