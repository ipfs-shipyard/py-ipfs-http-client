import pytest

import ipfshttpclient4ipwb


def test_assert_version():
	# Minimum required version
	ipfshttpclient4ipwb.assert_version("0.1.0", "0.1.0", "0.2.0", ["0.1.2"])
	
	# Too high version
	with pytest.raises(ipfshttpclient4ipwb.exceptions.VersionMismatch):
		ipfshttpclient4ipwb.assert_version("0.2.0", "0.1.0", "0.2.0", ["0.1.2"])
	
	# Too low version
	with pytest.raises(ipfshttpclient4ipwb.exceptions.VersionMismatch):
		ipfshttpclient4ipwb.assert_version("0.0.5", "0.1.0", "0.2.0", ["0.1.2"])
	
	# Blacklisted version
	with pytest.raises(ipfshttpclient.exceptions.VersionMismatch):
		ipfshttpclient.assert_version("0.1.2-1", "0.1.0", "0.2.0", ["0.1.2"])


def test_client_session_param():
	client = ipfshttpclient.Client(session=True)
	assert client._client._session is not None
	try:
		with pytest.raises(Exception):
			with client:
				pass  # Should fail because a session is already open
		assert client._client._session is not None
	finally:
		client.close()
	assert client._client._session is None


def test_client_session_context():
	client = ipfshttpclient.Client()
	assert client._client._session is None
	with client:
		assert client._client._session is not None
	assert client._client._session is None
