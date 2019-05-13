import pytest

import ipfshttpclient


def test_assert_version():
	# Minimum required version
	ipfshttpclient.assert_version("0.1.0", "0.1.0", "0.2.0", ["0.1.2"])
	
	# Too high version
	with pytest.raises(ipfshttpclient.exceptions.VersionMismatch):
		ipfshttpclient.assert_version("0.2.0", "0.1.0", "0.2.0", ["0.1.2"])
	
	# Too low version
	with pytest.raises(ipfshttpclient.exceptions.VersionMismatch):
		ipfshttpclient.assert_version("0.0.5", "0.1.0", "0.2.0", ["0.1.2"])
	
	# Blacklisted version
	with pytest.raises(ipfshttpclient.exceptions.VersionMismatch):
		ipfshttpclient.assert_version("0.1.2-1", "0.1.0", "0.2.0", ["0.1.2"])