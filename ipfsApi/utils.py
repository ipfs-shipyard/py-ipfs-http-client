"""A module to handle generic operations.

Classes:
return_field -- a decorator that returns the given field of a json response

Functions:
make_string_buffer -- returns a readable/writeable file-like object,
                      containing a given string value
encode_json -- returns a serialized Python object as a JSON encoded string
parse_json -- returns a Python object unserialized from JSON in json_str
make_json_buffer -- returns a file-like object containing a Python object
                    serialized to a JSON formatted string
encode_pyobj -- returns a serialized Python object as a Pickle encoded string
parse_pyobj -- returns a Python object unserialized from a
               Pickle encoded string
make_pyobj_buffer -- returns a file-like object containing a Python object
                     serialized to a Pickle formatted string
guess_mimetype -- guesses the mimetype of a file based on the filename
ls_dir -- returns files and subdirectories within a given directory
clean_file -- returns a tuple containing a file-like object and a boolean value
              indicating whether the file needs to be closed after use
clean_files -- generates tuples with a file-like object and a close indicator
file_size -- returns the size of a file in bytes
"""

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

    Keyword arguments:
    string -- desired content for the returned file-like object
    """
    if isinstance(string, six.text_type):
        buf = StringIO()
    else:
        buf = io.BytesIO()
    buf.write(string)
    buf.seek(0)
    return buf


def encode_json(py_obj):
    """Returns a serialized Python object as a JSON encoded string.

    Keyword arguments:
    py_obj -- any given Python object
    """
    return json.dumps(py_obj)


def parse_json(json_str):
    """Returns a Python object unserialized from JSON in json_str.

    >>> parse_json('[1, 2, 3, true, 4.5, null, 6e3]')
    [1, 2, 3, True, 4.5, None, 6000.0]

    Keyword arguments:
    json_str -- a JSON encoded string from which to reconstruct a Python object
    """
    return json.loads(json_str)


def make_json_buffer(py_obj):
    """Returns a file-like object containing py_obj as a JSON encoded string.

    >>> f = make_json_buffer([1, 2, 3, True, {u'distance': 4.5}])
    >>> f.read()
    '[1, 2, 3, true, {"distance": 4.5}]'

    Keyword arguments:
    py_obj -- any given Python object
    """
    return make_string_buffer(encode_json(py_obj))


def encode_pyobj(py_obj):
    """Returns a serialized Python object as a Pickle encoded string.

    Keyword arguments:
    py_obj -- any given Python object
    """
    return pickle.dumps(py_obj)


def parse_pyobj(pickled):
    r"""Returns a Python object unserialized from a Pickle encoded string.

    >>> parse_pyobj(b'(lp0\nI1\naI2\naI3\naI01\naF4.5\naNaF6000.0\na.')
    [1, 2, 3, True, 4.5, None, 6000.0]

    >>> parse_pyobj(u'(lp0\nI1\naI2\naI3\naI01\naF4.5\naNaF6000.0\na.')
    [1, 2, 3, True, 4.5, None, 6000.0]

    Keyword arguments:
    pickled -- the string of a pickled Python object to be reconstructed
    """
    if isinstance(pickled, six.text_type):
        pickled = pickled.encode('latin_1')
    return pickle.loads(pickled)


def make_pyobj_buffer(py_obj):
    """Returns a file-like object containing py_obj as a Pickle encoded string.

    >>> f = make_pyobj_buffer([1, 2, 3, True, 4.5, None, 6e3])
    >>> isinstance(f.read(), bytes)
    True

    Keyword arguments:
    py_obj -- any given Python object
    """
    return make_string_buffer(encode_pyobj(py_obj))


def guess_mimetype(filename):
    """Guesses the mimetype of a file based on the filename.

    >>> guess_mimetype('example.txt')
    'text/plain'
    >>> guess_mimetype('/foo/bar/example')
    'application/octet-stream'

    Keyword arguments:
    filename -- the file for which the mimetype is to be determined
    """
    fn = os.path.basename(filename)
    return mimetypes.guess_type(fn)[0] or 'application/octet-stream'


def ls_dir(dirname):
    """Returns files and subdirectories within a given directory.

    Returns a pair of lists, containing the names of directories and files
    in dirname

    Keyword arguments:
    dirname -- directory to be listed
    """
    ls = os.listdir(dirname)
    files = [p for p in ls if os.path.isfile(os.path.join(dirname, p))]
    dirs = [p for p in ls if os.path.isdir(os.path.join(dirname, p))]
    return files, dirs


def clean_file(f):
    """Returns a tuple containing a file-like object and a close indicator.

    This ensures the given file is opened and keeps track of files that should
    be closed after use (files that were not open prior to this function call).

    Keyword arguments:
    f -- a filepath or file-like object that may or may not need to be opened
    """
    if not hasattr(f, 'read'):
        return open(f, 'rb'), True
    else:
        return f, False


def clean_files(files):
    """Generates tuples with a file-like object and a close indicator.

    This is a generator of tuples, where the first element is the file object
    and the second element is a boolean which is True if this module opened the
    file (and thus should close it).

    Keyword arguments:
    files -- a list or tuple of filepaths and file-like objects
             or a singular instance of either a filepath or a file-like object
    """
    if isinstance(files, (list, tuple)):
        for f in files:
            yield clean_file(f)
    else:
        yield clean_file(files)


def file_size(f):
    """Returns the size of a file in bytes.

    Keyword arguments:
    f -- the file for which the size is to be determined
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
    """Decorator that returns the given field of a json response.

    Public methods:
    __init__ -- return_field constructor that sets the value of field
    __call__ -- wraps a command so that only the value of field is returned

    Instance variables:
    field -- the desired response field for a command that will be wrapped
    """
    def __init__(self, field):
        """Initializes a return_field object.

        Keyword arguments:
        field -- the response field to be returned for all function calls
        """
        self.field = field

    def __call__(self, cmd):
        """Wraps a command so that only a specified field is returned.

        Keyword arguments:
        cmd -- a command that is intended to be wrapped
        """
        @wraps(cmd)
        def wrapper(*args, **kwargs):
            """Returns the specified field of the command invocation.

            Keyword arguments:
            args -- additional arguments to cmd
            kwargs -- named additional arguments to cmd
            """
            res = cmd(*args, **kwargs)
            return res[self.field]
        return wrapper
