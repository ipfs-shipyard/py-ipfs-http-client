from __future__ import absolute_import

import io
import os
import json
import mimetypes

import six
from six.moves import cPickle as pickle
from six.moves import cStringIO as StringIO


def make_string_buffer(string):
    if isinstance(string, six.text_type):
        buf = StringIO()
    else:
        buf = io.BytesIO()
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
    if isinstance(pickled, six.text_type):
        pickled = pickled.encode('ascii')
    return pickle.loads(pickled)


def guess_mimetype(filename):
    fn = os.path.basename(filename)
    return mimetypes.guess_type(fn)[0] or 'application/octet-stream'


def ls_dir(dirname):
    ls = os.listdir(dirname)
    files = [p for p in ls if os.path.isfile(os.path.join(dirname, p))]
    dirs  = [p for p in ls if os.path.isdir(os.path.join(dirname, p))]
    return files, dirs
        

