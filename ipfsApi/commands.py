import os
import fnmatch
import functools
import mimetypes

from . import utils
from .exceptions import InvalidArguments, \
                        FileCommandException



class Command(object):
    
    def __init__(self, path, **defaults):
        self.path = path
        self.defaults = defaults

    def request(self, client, **kwargs):
        return client.request(self.path, **kwargs)

    def prepare(self, client, **kwargs):
        kwargs.update(self.defaults)
        return functools.partial(self.request, client, **kwargs)


class ArgCommand(Command):
    
    def __init__(self, path, argc=None, **defaults):
        Command.__init__(self, path, **defaults)
        self.argc = argc

    def request(self, client, args, **kwargs):
        if not isinstance(args, (list, tuple)):
            args = [args]
        if self.argc and len(args) != self.argc:
            raise InvalidArguments
        return client.request(self.path, args=args, **kwargs)


class FileCommand(Command):
    
    def request(self, client, f, **kwargs):
        if kwargs.pop('recursive', False):
            return self.recursive(client, f, **kwargs)
        if hasattr(f, '__iter__'):
            return self.multiple(client, f, **kwargs)
        if os.path.isdir(f):
            ls = [os.path.join(f,p) for p in os.listdir(f)]
            fs = filter(os.path.isfile, ls)
            return self.multiple(client, fs, **kwargs)
        else:
            return self.single(client, f, **kwargs)
   

    @staticmethod
    def _multipart_field(_file):
        try:
            content = _file.read()
            try:
                fn = _file.name
            except AttributeError:
                fn = ''
        except AttributeError:
            fn = _file
            if os.path.isdir(fn):
                raise FileCommandException("Use keyword argument [recursive=True] in order to add multiple directories.")
            with open(_file, 'rb') as fp:
                content = fp.read()
        ft = mimetypes.guess_type(fn)[0] or 'application/octet-stream'
        
        return ('file', (os.path.basename(fn), content, ft))

    
    def single(self, client, _file, **kwargs):
        """Adds a single file-like object to IPFS."""
        files = [self._multipart_field(_file)]
        return client.request(self.path, files=files, **kwargs)
   

    def multiple(self, client, _files, **kwargs):
        """Adds multiple file-like objects as a multipart request to IPFS."""
        fnpattern = kwargs.pop('match', '*')
        files = []
        for fn in _files:
            if not fnmatch.fnmatch(fn, fnpattern):
                continue
            files.append(self._multipart_field(fn))
        if not files:
            raise FileCommandException("No files matching pattern: {}".format(fnpattern))
        return client.request(self.path, files=files, **kwargs)


    def recursive(self, client, dirname, **kwargs):
        """Loads a directory recursively into IPFS, files are matched against
        the given pattern.
        
        ***NOTE: This is a ghetto temp solution until streaming multipart files
                 can be figured out.
        """
        kwargs.update({'decoder': 'json'})
        fnpattern = kwargs.pop('match', '*')
        results = []

        def fsize(fullpath):
            """This value is fudged to match the discrepancy between however
            the IPFS Api calculates file sizes and the value given by Python"""
            return os.path.getsize(fullpath) + 8
        
        def walk(dirname):
            ls = os.listdir(dirname)
            files = filter(lambda p: os.path.isfile(os.path.join(dirname, p)), ls)
            dirs  = filter(lambda p: os.path.isdir(os.path.join(dirname, p)), ls)
            
            dir_json = { u"Data": u'\x08\x01',
                        u"Links": []}

            for fn in files:
                if not fnmatch.fnmatch(fn, fnpattern):
                    continue
                fullpath = os.path.join(dirname, fn)
                res = client.request('/add',
                                     files=[self._multipart_field(fullpath)],
                                     **kwargs)
                
                res[u"Size"] = fsize(fullpath)
                dir_json[u"Links"].append(res)
                results.append({"Name": fullpath, "Hash": res[u"Hash"]})
            
            for subdir in dirs:
                fullpath = os.path.join(dirname, subdir)
                res = walk(fullpath)

                dir_json[u"Links"].append(res)
                results.append({"Name": fullpath, "Hash": res[u"Hash"]})
            
            buf = utils.make_json_buffer(dir_json)
            return client.request('/object/put',
                                  files=[self._multipart_field(buf)],
                                  **kwargs)
        
        # walk directory and then add final hash root to results
        res = walk(dirname)
        results.append({"Name": dirname, "Hash": res[u"Hash"]})
        return results
