IPFS API Bindings for Python
============================

Self-explanatory.  Check out `ipfs <http://ipfs.io/>`_ and `the command reference <http://ipfs.io/docs/commands/>`_ for more information on the IPFS Api.

This module also sports from helper function for adding non-files and even python objects to IPFS:

.. code-block:: python
    
    >>> import ipfs
    >>> api = ipfs.Client()
    >>> lst = [1, 77, 'lol']
    >>> api.add_pyobj(lst)
    u'QmRFqz1ABQtbMBDfjpMubTaginvpVnf58Y87gheRzGfe4i'
    >>> api.load_pyobj(_)
    [1, 77, 'lol']
    ...

More to come soon...

Things shouldn't be this way. Not in Python.

.. code-block:: python

    >>> r = requests.get('https://api.github.com', auth=('user', 'pass'))
    >>> r.status_code
    204
    >>> r.headers['content-type']
    'application/json'
    >>> r.text
    ...

See `the same code, without Requests <https://gist.github.com/973705>`_.
