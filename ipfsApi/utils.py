from __future__ import absolute_import

import io
import json
import mimetypes
import os
from functools import wraps

import six

from six.moves import cPickle as pickle
from six.moves import cStringIO as StringIO


def make_string_buffer(string):
    """Returns a readable/writeable file-like object, containing string.

    >>> f = make_string_buffer(u'text')
    >>> print(f.read())
    text

    If the string is a bytestring, then the returned object will
    operate in binary mode.

    >>> f = make_string_buffer(b'bytes')
    >>> f.read() == b'bytes'
    True
    """
    if isinstance(string, six.text_type):
        buf = StringIO()
    else:
        buf = io.BytesIO()
    buf.write(string)
    buf.seek(0)
    return buf


def encode_json(obj):
    return json.dumps(obj)


def parse_json(json_str):
    """Returns a Python object unserialized from JSON in json_str

    >>> parse_json('[1, 2, 3, true, 4.5, null, 6e3]')
    [1, 2, 3, True, 4.5, None, 6000.0]
    """
    return json.loads(json_str)


def make_json_buffer(json_obj):
    """Returns a file-like object containing json_obj serialized to JSON

    >>> f = make_json_buffer([1, 2, 3, True, {u'distance': 4.5}])
    >>> f.read()
    '[1, 2, 3, true, {"distance": 4.5}]'
    """
    return make_string_buffer(json.dumps(json_obj))


def encode_pyobj(py_obj):
    return pickle.dumps(py_obj)


def parse_pyobj(pickled):
    r"""Returns a Python object unpickled from the provided string

    >>> parse_pyobj(b'(lp0\nI1\naI2\naI3\naI01\naF4.5\naNaF6000.0\na.')
    [1, 2, 3, True, 4.5, None, 6000.0]

    >>> parse_pyobj(u'(lp0\nI1\naI2\naI3\naI01\naF4.5\naNaF6000.0\na.')
    [1, 2, 3, True, 4.5, None, 6000.0]
    """
    if isinstance(pickled, six.text_type):
        pickled = pickled.encode('latin_1')
    return pickle.loads(pickled)


def make_pyobj_buffer(py_obj):
    """Returns a file-like object containing py_obj serialized to a pickle

    >>> f = make_pyobj_buffer([1, 2, 3, True, 4.5, None, 6e3])
    >>> isinstance(f.read(), bytes)
    True
    """
    return make_string_buffer(pickle.dumps(py_obj))


def guess_mimetype(filename):
    """
    Guesses the mimetype of a file, based on the filename

    >>> guess_mimetype('example.txt')
    'text/plain'
    >>> guess_mimetype('/foo/bar/example')
    'application/octet-stream'
    """
    fn = os.path.basename(filename)
    return mimetypes.guess_type(fn)[0] or 'application/octet-stream'


def ls_dir(dirname):
    """
    Returns a pair of lists, containing the names of directories and files
    in dirname
    """
    ls = os.listdir(dirname)
    files = [p for p in ls if os.path.isfile(os.path.join(dirname, p))]
    dirs = [p for p in ls if os.path.isdir(os.path.join(dirname, p))]
    return files, dirs


def clean_file(f):
    """
    Returns a file object.
    """
    if not hasattr(f, 'read'):
        return open(f, 'rb'), True
    else:
        return f, False


def clean_files(files):
    """
    This is a generator of tuples, where the first element is the file object
    and the second element is a boolean which is True is this module opened the
    file (and thus should close it).
    """
    if isinstance(files, (list, tuple)):
        for f in files:
            yield clean_file(f)
    else:
        yield clean_file(files)


def file_size(f):
    """
    Returns size of file in bytes.
    """
    if isinstance(f, (six.string_types, six.text_type)):
        return os.path.getsize(f)
    else:
        cur = f.tell()
        f.seek(0, 2)
        size = f.tell()
        f.seek(cur)
        return size


class return_field(object):
    """
    Decorator that returns the given field of a json response.
    """
    def __init__(self, field):
        self.field = field

    def __call__(self, cmd):
        @wraps(cmd)
        def wrapper(api, *args, **kwargs):
            res = cmd(api, *args, **kwargs)
            return res[self.field]
        return wrapper
