
from ipfshttpclient.exceptions import MatcherSpecInvalidError, Error
from ipfshttpclient.filescanner import Matcher


def test_matcher_spec_invalid_error_message():
	ex = MatcherSpecInvalidError('junk')
	assert ex.args[0] == f"Don't know how to create a {Matcher.__name__} from spec 'junk'"


def test_matcher_spec_invalid_error_multiple_inheritance():
	ex = MatcherSpecInvalidError('wrong')

	# Base class of all exceptions in this library
	assert isinstance(ex, Error)

	# Base class of type errors
	assert isinstance(ex, TypeError)
