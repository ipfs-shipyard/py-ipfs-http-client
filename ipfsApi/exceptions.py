"""Defines the skeleton for exceptions.
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
