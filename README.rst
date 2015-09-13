.. image:: https://img.shields.io/pypi/v/ipfs-api.svg?style=flat-square

.. image:: https://img.shields.io/travis/ipfs/python-ipfs-api.svg?style=flat-square
    :target: https://travis-ci.org/ipfs/python-ipfs-api


IPFS API Bindings for Python
============================

Check out `ipfs <http://ipfs.io/>`_ and `the api command reference
<http://ipfs.io/docs/commands/>`_ for more information about the IPFS Api.

Install with pip:

.. code-block::

    pip install ipfs-api

Basic use-case (requires a running instance of IPFS daemon):

.. code-block:: python

    >>> import ipfsApi
    >>> api = ipfsApi.Client('127.0.0.1', 5001)
    >>> res = api.add('test.txt')
    >>> res
    {'Hash': 'QmWxS5aNTFEc9XbMX1ASvLET1zrqEaTssqt33rVZQCQb22', 'Name': 'test.txt'}
    >>> api.cat(res['Hash'])
    'fdsafkljdskafjaksdjf\n'

Administrative functions:

.. code-block:: python

    >>> api.id()
    {'Addresses': ['/ip4/127.0.0.1/tcp/4001/ipfs/QmS2C4MjZsv2iP1UDMMLCYqJ4WeJw8n3vXx1VKxW1UbqHS',
                   '/ip6/::1/tcp/4001/ipfs/QmS2C4MjZsv2iP1UDMMLCYqJ4WeJw8n3vXx1VKxW1UbqHS'],
     'AgentVersion': 'go-ipfs/0.3.8-dev',
     'ID': 'QmS2C4MjZsv2iP1UDMMLCYqJ4WeJw8n3vXx1VKxW1UbqHS',
     'ProtocolVersion': 'ipfs/0.1.0',
     'PublicKey': 'CAASpgIwgg ... 3FcjAgMBAAE='}

Pass in API options:

.. code-block:: python

    >>> api.pin_ls(opts={'type':'all'})
    {'Keys': {'QmNMELyizsfFdNZW3yKTi1SE2pErifwDTXx6vvQBfwcJbU': {'Count': 1,
                                                                 'Type': 'indirect'},
              'QmNQ1h6o1xJARvYzwmySPsuv9L5XfzS4WTvJSTAWwYRSd8': {'Count': 1,
                                                                 'Type': 'indirect'},
              ...

Add a directory and match against a filename pattern:

.. code-block:: python

    >>> api.add('photos', match='*.jpg')
    [{'Hash': 'QmcqBstfu5AWpXUqbucwimmWdJbu89qqYmE3WXVktvaXhX',
      'Name': 'photos/photo1.jpg'},
     {'Hash': 'QmSbmgg7kYwkSNzGLvWELnw1KthvTAMszN5TNg3XQ799Fu',
      'Name': 'photos/photo2.jpg'},
     {'Hash': 'Qma6K85PJ8dN3qWjxgsDNaMjWjTNy8ygUWXH2kfoq9bVxH',
      'Name': 'photos/photo3.jpg'}]

Or add a directory recursively:

.. code-block:: python

    >>> api.add('fake_dir', recursive=True)
    [{'Hash': 'QmQcCtMgLVwvMQGu6mvsRYLjwqrZJcYtH4mboM9urWW9vX',
      'Name': 'fake_dir/fsdfgh'},
     {'Hash': 'QmNuvmuFeeWWpxjCQwLkHshr8iqhGLWXFzSGzafBeawTTZ',
      'Name': 'fake_dir/test2/llllg'},
     {'Hash': 'QmX1dd5DtkgoiYRKaPQPTCtXArUu4jEZ62rJBUcd5WhxAZ',
      'Name': 'fake_dir/test2'},
     {'Hash': 'Qmenzb5J4fR9c69BbpbBhPTSp2Snjthu2hKPWGPPJUHb9M',
      'Name': 'fake_dir'}]

This module also contains some helper functions for adding strings, json, and even python objects to IPFS:

.. code-block:: python
    
    >>> lst = [1, 77, 'lol']
    >>> api.add_pyobj(lst)
    'QmRFqz1ABQtbMBDfjpMubTaginvpVnf58Y87gheRzGfe4i'
    >>> api.get_pyobj(_)
    [1, 77, 'lol']


How to Contribute
-----------------

IRC
~~~

Join us on IRC at ``#ipfs`` on `chat.freenode.net
<https://webchat.freenode.net>`_ if you have any suggestions or questions,
or if you just want to discuss IPFS and python.

Bug reports
~~~~~~~~~~~

You can submit bug reports using the `GitHub issue tracker
<https://github.com/ipfs/python-ipfs-api/issues>`_.

Pull requests
~~~~~~~~~~~~~

Pull requests are welcome.  Before submitting a new pull request, please
make sure that your code passes both the `pep8
<https://www.python.org/dev/peps/pep-0008/>`_ formatting check::

    $ tox -e pep8

And the unit tests::

    $ tox

You can arrange to run the pep8 tests automatically before each commit by
installing a ``pre-commit`` hook::

    $ ./tools/pre-commit --install

Please make sure to include new unit tests for new features or changes in
behavior.

License
-------

This code is distributed under the terms of the `MIT license
<https://opensource.org/licenses/MIT>`_.  Details can be found in the file
`LICENSE.txt <LICENSE.txt>`_ in this repository.
