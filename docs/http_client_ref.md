HTTP Client Reference
--------------------

All commands are accessed through the ``ipfshttpclient.Client`` class.

### Exceptions

```eval_rst
.. automodule:: ipfshttpclient.exceptions
    :members:
```



### The HTTP Client

All methods accept the following parameters in their ``kwargs``:

 * **opts** (*dict*) – A dictionary of custom parameters to be sent with the
                       HTTP request

```eval_rst
.. autofunction:: ipfshttpclient.connect

.. autofunction:: ipfshttpclient.assert_version

.. autoclientclass:: ipfshttpclient.Client
	:members:
	:inherited-members:
	:undoc-members:
```
