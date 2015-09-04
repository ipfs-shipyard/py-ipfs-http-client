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
