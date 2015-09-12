from __future__ import absolute_import

import os
import json
import mimetypes
import cPickle as pickle
from cStringIO import StringIO


def make_string_buffer(string):
    buf = StringIO()
    buf.write(string)
    buf.seek(0)
    return buf

def make_json_buffer(json_obj):
    return make_string_buffer(json.dumps(json_obj))

def parse_json(json_str):
    return json.loads(json_str)

def make_pyobj_buffer(py_obj):
    return make_string_buffer(pickle.dumps(py_obj))

def parse_pyobj(pickled):
    return pickle.loads(str(pickled))


def guess_mimetype(filename):
    fn = os.path.basename(filename)
    return mimetypes.guess_type(fn)[0] or 'application/octet-stream'


def ls_dir(dirname):
    ls = os.listdir(dirname)
    files = filter(lambda p: os.path.isfile(os.path.join(dirname, p)), ls)
    dirs  = filter(lambda p: os.path.isdir(os.path.join(dirname, p)), ls)
    return files, dirs
        

