import os
from os import path
import fnmatch
import mimetypes

def recursive_glob(root, pattern):
    results = []
    for base, dirs, files in os.walk(root):
        goodfiles = fnmatch.filter(files, pattern)
        results.extend(os.path.join(base, f) for f in goodfiles)
    return results


def _make_file_fields(files):
    fields = []
    for item in files:
        if isinstance(item, tuple):
            fn = item[0]
            fp = open(fn, 'rb')
            ft = item[1]
        else:
            fn = item
            fp = open(fn, 'rb')
            ft = mimetypes.guess_type(fn)[0]
        
        name = path.basename(fn) 

        t = (name, fp, ft) if ft else (fn, fp)

        fields.append(('file', t))
    
    return fields


def _close_files(fields):
    for t in fields:
        t[1][1].close()



files = _make_file_fields(recursive_glob('test', '*'))

params = {'stream-channels': 'true'}

r = requests.get('http://127.0.0.1:5001/api/v0/add', files=files, params=params)

print r.request.body

print r.text

_close_files(files)


