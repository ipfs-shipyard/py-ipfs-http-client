"""A module to handle generic operations.
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

    .. code-block:: python

        >>> f = make_string_buffer(u'text')
        >>> print(f.read())
        text

    If the string is a bytestring, then the returned object will
    operate in binary mode.

    .. code-block:: python

        >>> f = make_string_buffer(b'bytes')
        >>> f.read() == b'bytes'
        True

    Parameters
    ----------
    string : str | bytes
        Desired content for the returned ``file``-like object
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

    Parameters
    ----------
    py_obj : dict | str | list | int
        A JSON-encodable Python object
    """
    return json.dumps(py_obj)


def parse_json(json_str):
    """Returns a Python object unserialized from JSON in ``json_str``.

    .. code-block:: python

        >>> parse_json('[1, 2, 3, true, 4.5, null, 6e3]')
        [1, 2, 3, True, 4.5, None, 6000.0]

    Parameters
    ----------
    json_str : str
        A JSON encoded string from which to create a Python object
    """
    return json.loads(json_str)


def make_json_buffer(py_obj):
    """Returns a ``file``-like object containing ``py_obj`` as a JSON encoded
    string.

    .. code-block:: python

        >>> f = make_json_buffer([1, 2, 3, True, {u'distance': 4.5}])
        >>> f.read()
        '[1, 2, 3, true, {"distance": 4.5}]'

    Parameters
    ----------
    py_obj : dict | str | list | int
        A JSON-encodable Python object
    """
    return make_string_buffer(encode_json(py_obj))


def encode_pyobj(py_obj):
    """Returns a serialized Python object as a Pickle encoded string.

    Parameters
    ----------
    py_obj : object
        A serilizable Python object
    """
    return pickle.dumps(py_obj)


def parse_pyobj(pickled):
    r"""Returns a Python object unserialized from a Pickle encoded string.

    .. code-block:: python

        >>> parse_pyobj(b'(lp0\nI1\naI2\naI3\naI01\naF4.5\naNaF6000.0\na.')
        [1, 2, 3, True, 4.5, None, 6000.0]

        >>> parse_pyobj(u'(lp0\nI1\naI2\naI3\naI01\naF4.5\naNaF6000.0\na.')
        [1, 2, 3, True, 4.5, None, 6000.0]

    Parameters
    ----------
    pickled : bytes
        The string of a pickled Python object to be reconstructed
    """
    if isinstance(pickled, six.text_type):
        pickled = pickled.encode('latin_1')
    return pickle.loads(pickled)


def make_pyobj_buffer(py_obj):
    """Returns a file-like object containing py_obj as a Pickle encoded string.

    .. code-block:: python

        >>> f = make_pyobj_buffer([1, 2, 3, True, 4.5, None, 6e3])
        >>> isinstance(f.read(), bytes)
        True

    Parameters
    ----------
    py_obj : object
        A serilizable Python object
    """
    return make_string_buffer(encode_pyobj(py_obj))


def guess_mimetype(filename):
    """Guesses the mimetype of a file based on the given ``filename``.

    .. code-block:: python

        >>> guess_mimetype('example.txt')
        'text/plain'
        >>> guess_mimetype('/foo/bar/example')
        'application/octet-stream'

    Parameters
    ----------
    filename : str
        The file name or path for which the mimetype is to be guessed
    """
    fn = os.path.basename(filename)
    return mimetypes.guess_type(fn)[0] or 'application/octet-stream'


def ls_dir(dirname):
    """Returns files and subdirectories within a given directory.

    Returns a pair of lists, containing the names of directories and files
    in ``dirname``.

    Parameters
    ----------
    dirname : str
        The path of the directory to be listed
    """
    ls = os.listdir(dirname)
    files = [p for p in ls if os.path.isfile(os.path.join(dirname, p))]
    dirs = [p for p in ls if os.path.isdir(os.path.join(dirname, p))]
    return files, dirs


def clean_file(file):
    """Returns a tuple containing a ``file``-like object and a close indicator.

    This ensures the given file is opened and keeps track of files that should
    be closed after use (files that were not open prior to this function call).

    Parameters
    ----------
    file : str | io.IOBase
        A filepath or ``file``-like object that may or may not need to be
        opened
    """
    if not hasattr(file, 'read'):
        return open(file, 'rb'), True
    else:
        return file, False


def clean_files(files):
    """Generates tuples with a ``file``-like object and a close indicator.

    This is a generator of tuples, where the first element is the file object
    and the second element is a boolean which is True if this module opened the
    file (and thus should close it).

    Parameters
    ----------
    files : list | io.IOBase | str
        Collection or single instance of a filepath and file-like object
    """
    if isinstance(files, (list, tuple)):
        for f in files:
            yield clean_file(f)
    else:
        yield clean_file(files)


def file_size(f):
    """Returns the size of a file in bytes.

    Parameters
    ----------
    f : io.IOBase | str
        The file path or object for which the size should be determined
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

    Parameters
    ----------
    field : object
        The response field to be returned for all invocations
    """
    def __init__(self, field):
        self.field = field

    def __call__(self, cmd):
        """Wraps a command so that only a specified field is returned.

        Parameters
        ----------
        cmd : callable
            A command that is intended to be wrapped
        """
        @wraps(cmd)
        def wrapper(*args, **kwargs):
            """Returns the specified field of the command invocation.

            Parameters
            ----------
            args : list
                Positional parameters to pass to the wrapped callable
            kwargs : dict
                Named parameter to pass to the wrapped callable
            """
            res = cmd(*args, **kwargs)
            return res[self.field]
        return wrapper
