"""
IPFS API Bindings for Python
"""
import os
import functools
import requests
import mimetypes
import cPickle as pickle
import json
from cStringIO import StringIO



class InvalidEndpoint(Exception):
    pass

class InvalidCommand(Exception):
    pass

class InvalidArguments(Exception):
    pass



class Command(object):
    def __init__(self, path, **kwargs):
        self.path = path
        self._defaults = kwargs

    def _request(self, client, **kwargs):
        return client.request(self.path, **kwargs)

    def get_ctx(self, client):
        return functools.partial(self._request, client, **self._defaults)



class ArgCommand(Command):
    def __init__(self, path, argc=None):
        Command.__init__(self, path)
        self.argc = argc

    def _request(self, client, args, **kwargs):
        
        if not isinstance(args, (list, tuple)):
            args = [args]
        if self.argc and len(args)>self.argc:
            raise InvalidArguments
        
        return client.request(self.path, args, **kwargs)
        


class HTTPClient(object):

    def __init__(self, host, port, base):
        self.host = host
        self.port = port
        self.base = 'http://%s:%s/%s' % (host, port, base)


    def request(self, path, args=[], opts=[], files=[], json=False):
        
        url = self.base + path
        
        params = []
        params.append(('stream-channels', 'true'))
        params.append((       'encoding', 'json'))
        
        for opt in opts:
            params.append(opt)

        for arg in args:
            params.append(('arg', arg))

        method = 'post' if files else 'get'

        res = requests.request(method, url, params=params)

        if json: return res.json()
        return res.text




class Client(object):

    def __init__(self, host='127.0.0.1', port=5001, base='api/v0'):

        self._http_client = HTTPClient(host, port, base)


        ############
        # COMMANDS #
        ############
        
        # BASIC COMMANDS
        #self.add                = FileCommand('/add')
        self.cat                =  ArgCommand('/cat')
        self.ls                 =  ArgCommand('/ls')
        self.refs               =  ArgCommand('/refs')
        
        # DATA STRUCTURE COMMANDS
        self.block_stat         =  ArgCommand('/block/stat')
        self.block_get          =  ArgCommand('/block/get')
        #self.block_put          = FileCommand('/block/put')
        self.object_data        =  ArgCommand('/object/data')
        self.object_links       =  ArgCommand('/object/links')
        self.object_get         =  ArgCommand('/object/get')
        #self.object_put         = FileCommand('/object/put')
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

        # NETWORK COMMANDS
        self.id                 =     Command('/id')
        self.bootstrap          =     Command('/bootstrap')
        self.swarm_peers        =     Command('/swarm/peers', json=True)
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
        """Pass HTTPClient context to command or intercept
        AttributeError."""
        if name == "_http_client":
            return object.__getattribute__(self, name)
        try:
            cmd = object.__getattribute__(self, name)
            return cmd.get_ctx(self._http_client)
        except AttributeError:
            raise InvalidCommand




if __name__ == "__main__":
    api = Client()
    
    print api.swarm_peers()
    print api.cat('Qmf3sE2DaCSEc9XVr9yro9Y4Sj5Ac8rgjqqWYAsC2c9FrV')
