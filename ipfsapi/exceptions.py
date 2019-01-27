# -*- coding: utf-8 -*-
"""
The class hierachy for exceptions is::

    Error
     +-- VersionMismatch
     +-- EncoderError
     |    +-- EncoderMissingError
     |    +-- EncodingError
     |    +-- DecodingError
     +-- CommunicationError
          +-- ProtocolError
          +-- StatusError
          +-- ErrorResponse
          +-- ConnectionError
          +-- TimeoutError

"""
# Delegate list of exceptions to `ipfshttpclient`
from ipfshttpclient.exceptions import *
__all__ = [
	"Error",
	"VersionMismatch",
	"EncoderError",
	"EncoderMissingError",
	"EncodingError",
	"DecodingError",
	"CommunicationError",
	"ProtocolError",
	"StatusError",
	"ErrorResponse",
	"ConnectionError",
	"TimeoutError"
]