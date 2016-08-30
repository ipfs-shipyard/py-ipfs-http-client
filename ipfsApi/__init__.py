from __future__ import absolute_import

__version__ = '0.2.3'

###########################
# Import stable API parts #
###########################
from . import exceptions

from .client import DEFAULT_HOST, DEFAULT_PORT, DEFAULT_BASE
from .client import VERSION_MINIMUM, VERSION_MAXIMUM
from .client import Client, assert_version, connect
