# Note that this file is special in that py.test will automatically import this file and gather
# its list of fixtures even if it is not directly imported into the corresponding test case.
import pathlib

import pytest

import ipfshttpclient


TEST_DIR = pathlib.Path(__file__).parent


__is_available = None
def is_available():  # noqa
	"""
	Return whether the IPFS daemon is reachable or not
	"""
	global __is_available

	if not isinstance(__is_available, bool):
		try:
			ipfshttpclient.connect()
		except ipfshttpclient.exceptions.Error as error:
			__is_available = False

			# Make sure version incompatiblity is displayed to the user
			if isinstance(error, ipfshttpclient.exceptions.VersionMismatch):
				raise
		else:
			__is_available = True

	return __is_available


def sort_by_key(items, key="Name"):
	return sorted(items, key=lambda x: x[key])



@pytest.fixture
def client():
	if is_available():
		return ipfshttpclient.Client()
	else:
		pytest.skip("Running IPFS node required")


@pytest.fixture
def cleanup_pins(client):
	pinned = set(client.pin.ls(type="recursive")["Keys"])
	
	yield
	
	for multihash in client.pin.ls(type="recursive")["Keys"]:
		if multihash not in pinned:
			client.pin.rm(multihash)