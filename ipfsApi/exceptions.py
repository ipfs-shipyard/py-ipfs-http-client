class ipfsApiError(Exception):
    pass


class InvalidCommand(ipfsApiError):
    pass


class InvalidArguments(ipfsApiError):
    pass


class InvalidPath(ipfsApiError):
    pass


class FileCommandException(ipfsApiError):
    pass


class EncodingException(ipfsApiError):
    pass
