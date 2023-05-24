
import pytest

from ipfshttpclient.exceptions import ErrorResponse, StatusError
from ipfshttpclient.http_common import ClientSyncBase


def test_client_sync_base_raises_for_standardized_failure():
	original = Exception('foo')

	with pytest.raises(ErrorResponse) as failure:
		ClientSyncBase._raise_for_response_status(
			error=original,
			status_code=405,
			content=[
				{
					'Message': 'bar'
				}
			]
		)

	assert failure.value.status_code == 405
	assert str(failure.value) == 'bar'
	assert failure.value.original is original


@pytest.mark.parametrize('content', [
	[],
	[{'wrong': 'ignored'}],
	[{'Message': 'too'}, {'Message': 'many'}]
])
def test_client_sync_base_raises_for_non_standard_failure(content):
	original = Exception('qux')

	with pytest.raises(StatusError) as failure:
		ClientSyncBase._raise_for_response_status(
			error=original,
			status_code=406,
			content=content
		)

	assert failure.value.status_code == 406
	assert str(failure.value) == 'qux'
	assert failure.value.original is original
