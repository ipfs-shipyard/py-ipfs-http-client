"""Defines the skeleton for exceptions.
"""


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class InvalidCommand(Error):
    """Exception raised for an invalid command."""
    pass


class InvalidArguments(Error):
    """Exception raised for invalid arguments."""
    pass


class InvalidPath(Error):
    """Exception raised for an invalid path."""
    pass


class FileCommandException(Error):
    """Exception raised for file command exception."""
    pass


class EncodingException(Error):
    """Exception raised for invalid encoding."""
    pass
