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


def get_client(offline=False):
	if is_available():
		return ipfshttpclient.Client(offline=offline)
	else:
		pytest.skip("Running IPFS node required")


@pytest.fixture(scope="function")
def client():
	"""Create a client with function lifetimme to connect to the IPFS daemon.

	Each test function should instantiate a fresh client, so use this
	fixture in test functions."""
	with get_client() as client:
		yield client


@pytest.fixture(scope="function")
def offline_client():
	"""Create a client in offline mode with function lifetimme"""
	with get_client(offline=True) as client:
		yield client


@pytest.fixture(scope="module")
def module_client():
	"""Create a client with a module lifetime to connect to the IPFS daemon.

	For module-scope fixtures that need a client, if the client is to be created
	automatically using a fixture (to keep client creation code centralized
	here), that client-creating fixture must also be module-scope, so use
	this fixture in module-scoped fixtures."""
	with get_client() as client:
		yield client


@pytest.fixture(scope="module")
def module_offline_client():
	"""Create a client in offline mode with module lifetime."""
	with get_client(offline=True) as client:
		yield client


@pytest.fixture
def cleanup_pins(client):
	pinned = set(client.pin.ls(type="recursive")["Keys"])
	
	yield
	
	for multihash in client.pin.ls(type="recursive")["Keys"]:
		if multihash not in pinned:
			client.pin.rm(multihash)