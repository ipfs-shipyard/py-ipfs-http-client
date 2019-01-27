"""Python IPFS API client library"""

from __future__ import absolute_import

import warnings
warnings.warn(
	"The `ipfsapi` library is deprecated and will stop receiving updates on "
	"the 31.12.2019! If you are on Python 3.5+ please enable and fix all "
	"Python deprecation warnings (CPython flag `-Wd`) and switch to the new "
	"`ipfshttpclient` library name. Python 2.7 and 3.4 will not be supported "
	"by the new library, so please upgrade.", FutureWarning, stacklevel=2
)

from .version import __version__

###########################
# Import stable API parts #
###########################
from . import exceptions

from .client import DEFAULT_HOST, DEFAULT_PORT, DEFAULT_BASE
from .client import VERSION_MINIMUM, VERSION_MAXIMUM
from .client import Client, assert_version, connect
