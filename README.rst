IPFS API Bindings for Python
============================

Self-explanatory.  Check out `ipfs <http://ipfs.io/>`_ and `the command reference <http://ipfs.io/docs/commands/>`_ for more information about the IPFS Api.

Basic use-case:

.. code-block:: python

    >>> import ipfs
    >>> api = ipfs.Client('127.0.0.1', 5001)
    >>> res = api.add('test.txt')
    >>> res
    {u'Hash': u'QmWxS5aNTFEc9XbMX1ASvLET1zrqEaTssqt33rVZQCQb22', u'Name': u'test.txt'}
    >>> api.cat(res['Hash'])
    u'fdsafkljdskafjaksdjf\n'


Administrative functions:

.. code-block:: python

    >>> api.id()
    {u'Addresses': [u'/ip4/127.0.0.1/tcp/4001/ipfs/QmS2C4MjZsv2iP1UDMMLCYqJ4WeJw8n3vXx1VKxW1UbqHS',
                    u'/ip4/162.243.155.215/tcp/4001/ipfs/QmS2C4MjZsv2iP1UDMMLCYqJ4WeJw8n3vXx1VKxW1UbqHS',
                    u'/ip6/::1/tcp/4001/ipfs/QmS2C4MjZsv2iP1UDMMLCYqJ4WeJw8n3vXx1VKxW1UbqHS'],
     u'AgentVersion': u'go-ipfs/0.3.8-dev',
     u'ID': u'QmS2C4MjZsv2iP1UDMMLCYqJ4WeJw8n3vXx1VKxW1UbqHS',
     u'ProtocolVersion': u'ipfs/0.1.0',
     u'PublicKey': u'CAASpgIwgg ... 3FcjAgMBAAE='}

Pass in API options:

.. code-block:: python

    >>> api.pin_ls(opts={'type':'all'})
    {u'Keys': {u'QmNMELyizsfFdNZW3yKTi1SE2pErifwDTXx6vvQBfwcJbU': {u'Count': 1,
                                                                   u'Type': u'indirect'},
               u'QmNQ1h6o1xJARvYzwmySPsuv9L5XfzS4WTvJSTAWwYRSd8': {u'Count': 1,
                                                                   u'Type': u'indirect'},
    ...

This module also contains some helper functions for adding strings, json, and even python objects to IPFS:

.. code-block:: python
    
    >>> lst = [1, 77, 'lol']
    >>> api.add_pyobj(lst)
    u'QmRFqz1ABQtbMBDfjpMubTaginvpVnf58Y87gheRzGfe4i'
    >>> api.load_pyobj(_)
    [1, 77, 'lol']

More to come soon...
