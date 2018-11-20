Client API Reference
--------------------

All commands are accessed through the ``ipfsapi.Client`` class.

### Exceptions

```eval_rst
.. automodule:: ipfsapi.exceptions
    :members:
```



### The API Client

All methods accept the following parameters in their ``kwargs``:

 * **opts** (*dict*) – A dictonary of custom parameters to be sent with the
                       HTTP request

```eval_rst
.. autofunction:: ipfsapi.connect

.. autofunction:: ipfsapi.assert_version

.. autoclass:: ipfsapi.Client
    :members:
    :show-inheritance:

```
