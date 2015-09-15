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

        self._client = self._clientfactory(host, port, base, default_enc)

        # default request keyword-args
        if 'opts' in defaults:
            defaults['opts'].update({'encoding': default_enc})
        else:
            defaults.update({'opts': {'encoding': default_enc}})

        self._defaults = defaults

    # BASIC COMMANDS
    def add(self, *args, **kwargs):
        """
        """
        return FileCommand('/add')(self._client, *args, **kwargs)

    def cat(self, *args, **kwargs):
        """
        """
        return ArgCommand('/cat')(self._client, *args, **kwargs)

    def ls(self, *args, **kwargs):
        """
        """
        return ArgCommand('/ls')(self._client, *args, **kwargs)

    def refs(self, *args, **kwargs):
        """
        """
        return ArgCommand('/refs')(self._client, *args, **kwargs)

    # DATA STRUCTURE COMMANDS
    def block_stat(self, *args, **kwargs):
        """  """
        return ArgCommand('/block/stat')(self._client, *args, **kwargs)

    def block_get(self, *args, **kwargs):
        """  """
        return ArgCommand('/block/get')(self._client, *args, **kwargs)

    def block_put(self, *args, **kwargs):
        """  """
        return FileCommand('/block/put', accept_multiple=False
                           )(self._client, *args, **kwargs)

    def object_data(self, *args, **kwargs):
        """  """
        return ArgCommand('/object/data')(self._client, *args, **kwargs)

    def object_links(self, *args, **kwargs):
        """  """
        return ArgCommand('/object/links')(self._client, *args, **kwargs)

    def object_get(self, *args, **kwargs):
        """  """
        return ArgCommand('/object/get')(self._client, *args, **kwargs)

    def object_put(self, *args, **kwargs):
        """  """
        return FileCommand('/object/put')(self._client, *args, **kwargs)

    def object_stat(self, *args, **kwargs):
        """  """
        return ArgCommand('/object/stat')(self._client, *args, **kwargs)

    def object_patch(self, *args, **kwargs):
        """  """
        return ArgCommand('/object/patch')(self._client, *args, **kwargs)

    def file_ls(self, *args, **kwargs):
        """  """
        return ArgCommand('/file/ls')(self._client, *args, **kwargs)

    # ADVANCED COMMANDS
    def resolve(self, *args, **kwargs):
        """  """
        return ArgCommand('/resolve')(self._client, *args, **kwargs)

    def name_publish(self, *args, **kwargs):
        """  """
        return ArgCommand('/name/publish')(self._client, *args, **kwargs)

    def name_resolve(self, *args, **kwargs):
        """  """
        return ArgCommand('/name/resolve')(self._client, *args, **kwargs)

    def dns(self, *args, **kwargs):
        """  """
        return ArgCommand('/dns')(self._client, *args, **kwargs)

    def pin_add(self, *args, **kwargs):
        """  """
        return ArgCommand('/pin/add')(self._client, *args, **kwargs)

    def pin_rm(self, *args, **kwargs):
        """  """
        return ArgCommand('/pin/rm')(self._client, *args, **kwargs)

    def pin_ls(self, *args, **kwargs):
        """  """
        return Command('/pin/ls')(self._client, *args, **kwargs)

    def repo_gc(self, *args, **kwargs):
        """  """
        return Command('/repo/gc')(self._client, *args, **kwargs)

    # NETWORK COMMANDS
    def id(self, *args, **kwargs):
        """  """
        return Command('/id')(self._client, *args, **kwargs)

    def bootstrap(self, *args, **kwargs):
        """  """
        return Command('/bootstrap')(self._client, *args, **kwargs)

    def bootstrap_add(self, *args, **kwargs):
        """  """
        return ArgCommand('/bootstrap/add')(self._client, *args, **kwargs)

    def bootstrap_rm(self, *args, **kwargs):
        """  """
        return ArgCommand('/bootstrap/rm')(self._client, *args, **kwargs)

    def swarm_peers(self, *args, **kwargs):
        """  """
        return Command('/swarm/peers')(self._client, *args, **kwargs)

    def swarm_addrs(self, *args, **kwargs):
        """  """
        return Command('/swarm/addrs')(self._client, *args, **kwargs)

    def swarm_connect(self, *args, **kwargs):
        """  """
        return ArgCommand('/swarm/connect')(self._client, *args, **kwargs)

    def swarm_disconnect(self, *args, **kwargs):
        """  """
        return ArgCommand('/swarm/disconnect')(self._client, *args, **kwargs)

    def swarm_filters_add(self, *args, **kwargs):
        """  """
        return ArgCommand('/swarm/filters/add')(self._client, *args, **kwargs)

    def swarm_filters_rm(self, *args, **kwargs):
        """  """
        return ArgCommand('/swarm/filters/rm')(self._client, *args, **kwargs)

    def dht_query(self, *args, **kwargs):
        """  """
        return ArgCommand('/dht/query')(self._client, *args, **kwargs)

    def dht_findprovs(self, *args, **kwargs):
        """  """
        return ArgCommand('/dht/findprovs')(self._client, *args, **kwargs)

    def dht_findpeer(self, *args, **kwargs):
        """  """
        return ArgCommand('/dht/findpeer')(self._client, *args, **kwargs)

    def dht_get(self, *args, **kwargs):
        """  """
        return ArgCommand('/dht/get', decoder='json',
                          post_hook=lambda r: r[u"Extra"])(self,
                                                           **kwargs)

    def dht_put(self, *args, **kwargs):
        """  """
        return ArgCommand('/dht/put', argc=2)(self._client, *args, **kwargs)

    def ping(self, *args, **kwargs):
        """  """
        return ArgCommand('/ping')(self._client, *args, **kwargs)

    # TOOL COMMANDS
    def config(self, *args, **kwargs):
        """  """
        return ArgCommand('/config')(self._client, *args, **kwargs)

    def config_show(self, *args, **kwargs):
        """  """
        return Command('/config/show')(self._client, *args, **kwargs)

    def config_replace(self, *args, **kwargs):
        """  """
        return ArgCommand('/config/replace')(self._client, *args, **kwargs)

    def version(self, *args, **kwargs):
        """  """
        return Command('/version')

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
