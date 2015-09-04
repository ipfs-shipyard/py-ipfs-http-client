"""
IPFS API Bindings for Python
"""
import os
import functools
import requests
import mimetypes
import json
import cPickle as pickle
from cStringIO import StringIO



class InvalidCommand(Exception):
    pass

class InvalidArguments(Exception):
    pass



class Command(object):
    
    def __init__(self, path, **defaults):
        self.path = path
        self.defaults = defaults

    def request(self, client, **kwargs):
        return client.request(self.path, **kwargs)

    def prepare(self, client):
        return functools.partial(self.request, client, **self.defaults)


class ArgCommand(Command):
    
    def __init__(self, path, argc=None, **defaults):
        Command.__init__(self, path, **defaults)
        self.argc = argc

    def request(self, client, args, **kwargs):
        if not isinstance(args, (list, tuple)):
            args = [args]
        if self.argc and len(args) != self.argc:
            raise InvalidArguments
        return client.request(self.path, args, **kwargs)


class FileCommand(Command):
    
    def request(self, client, fp_or_fn, **kwargs):
        try:
            content = fp_or_fn.read()
            try:
                fn = fp_or_fn.name
            except AttributeError:
                fn = 'StringIO'
        except AttributeError:
            fn = fp_or_fn
            with open(fn, 'rb') as fp:
                content = fp.read()
        
        files = [('file', (fn, content, 'application/octet-stream'))]
        
        return client.request(self.path, files=files, **kwargs)



class HTTPClient(object):

    def __init__(self, host, port, base):
        self.host = host
        self.port = port
        self.base = 'http://%s:%s/%s' % (host, port, base)

    def request(self, path, args=[], opts=[], files=[], json=True):
        
        url = self.base + path
        
        params = []
        params.append(('stream-channels', 'true'))
        
        if json:
            params.append(('encoding', 'json'))
        
        for opt in opts:
            params.append(opt)

        for arg in args:
            params.append(('arg', arg))

        method = 'post' if files else 'get'

        res = requests.request(method, url, params=params, files=files)

        if json:
            try:
                return res.json()
            except:
                pass
        
        return res.text




class Client(object):

    def __init__(self, host='127.0.0.1', port=5001, base='api/v0'):

        self._http_client = HTTPClient(host, port, base)


        ############
        # COMMANDS #
        ############
        
        # BASIC COMMANDS
        self.add                = FileCommand('/add')
        self.cat                =  ArgCommand('/cat', json=False)
        self.ls                 =  ArgCommand('/ls')
        self.refs               =  ArgCommand('/refs')
        
        # DATA STRUCTURE COMMANDS
        self.block_stat         =  ArgCommand('/block/stat')
        self.block_get          =  ArgCommand('/block/get')
        self.block_put          = FileCommand('/block/put')
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
        self.name_resolve       =     Command('/name/resolve')
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
        self.dht_get            =  ArgCommand('/dht/get')
        self.dht_put            =  ArgCommand('/dht/put', argc=2)
        self.ping               =  ArgCommand('/ping')
        
        # TOOL COMMANDS
        self.config             =  ArgCommand('/config')
        self.config_show        =     Command('/config/show')
        self.config_replace     =  ArgCommand('/config/replace')
        self.version            =     Command('/version')


    def __getattribute__(self, name):
        """Prepares command context or raises InvalidCommand
        exception."""
        try:
            attr = object.__getattribute__(self, name)
            if isinstance(attr, Command):
                return attr.prepare(self._http_client)
            else:
                return attr
        except AttributeError:
            raise InvalidCommand


    ###########
    # HELPERS #
    ###########
    @staticmethod
    def make_buffer(string):
        buf = StringIO()
        buf.write(string)
        buf.seek(0)
        return buf

    def add_str(self, string, **kwargs):
        """Adds a Python string as a file to IPFS."""
        return self.add(self.make_buffer(string), **kwargs)
    
    def add_json(self, json_obj, **kwargs):
        """Adds a json-serializable Python dict as a json file to IPFS."""
        return self.add(self.make_buffer(json.dumps(json_obj)), **kwargs)
    
    def load_json(self, multihash, **kwargs):
        """Loads a json object from IPFS."""
        return self.cat(multihash, json=True, **kwargs)

    def add_pyobj(self, py_obj, **kwargs):
        """Adds a picklable Python object as a file to IPFS."""
        return self.add(self.make_buffer(pickle.dumps(py_obj)), **kwargs)

    def load_pyobj(self, multihash, **kwargs):
        """Loads a pickled Python object from IPFS."""
        return pickle.loads(self.cat(multihash, **kwargs))


