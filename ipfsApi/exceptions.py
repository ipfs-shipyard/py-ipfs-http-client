"""Defines the skeleton for exceptions.

Classes:
ipfsApiError - A base class for generic exceptions.
InvalidCommand - An ipfsApiError subclass for invalid commands.
InvalidArguments - An ipfsApiError subclass for invalid arguments.
InvalidPath - An ipfsApiError subclass for invalid path.
FileCommandException - An ipfsApiError subclass for file command exceptions.
EncodingException - An ipfsApiError subclass for encoding exceptions.
"""


class ipfsApiError(Exception):
    """Base class for exceptions in this module."""
    pass


class InvalidCommand(ipfsApiError):
    """Exception raised for an invalid command."""
    pass


class InvalidArguments(ipfsApiError):
    """Exception raised for invalid arguments."""
    pass


class InvalidPath(ipfsApiError):
    """Exception raised for an invalid path."""
    pass


class FileCommandException(ipfsApiError):
    """Exception raised for file command exception."""
    pass


class EncodingException(ipfsApiError):
    """Exception raised for invalid encoding."""
    pass
