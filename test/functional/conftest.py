# Note that this file is special in that py.test will automatically import this file and gather
# its list of fixtures even if it is not directly imported into the corresponding test case.

import pathlib
import pytest
import sys
import typing as ty

import ipfshttpclient


TEST_DIR: pathlib.Path = pathlib.Path(__file__).parent


@pytest.fixture(scope='session')
def fake_dir() -> pathlib.Path:
	return TEST_DIR.joinpath('fake_dir')


@pytest.fixture(scope='session')
def ipfs_is_available() -> bool:
	"""
	Return whether the IPFS daemon is reachable or not
	"""

	try:
		with ipfshttpclient.connect():
			pass
	except ipfshttpclient.exceptions.Error as e:
		print('\nFailed to connect to IPFS client', file=sys.stderr)
		print(e, file=sys.stderr)

		return False
	else:
		return True


def sort_by_key(items, key="Name"):
	return sorted(items, key=lambda x: x[key])


def _generate_client(
		ipfs_is_available: bool,
		offline: bool
) -> ty.Generator[ipfshttpclient.Client, None, None]:
	if ipfs_is_available:
		with ipfshttpclient.Client(offline=offline) as client:
			yield client
	else:
		pytest.skip("Running IPFS node required")


@pytest.fixture(scope="function")
def client(ipfs_is_available: bool):
	yield from _generate_client(ipfs_is_available, False)


@pytest.fixture(scope="function")
def offline_client(ipfs_is_available: bool):
	yield from _generate_client(ipfs_is_available, True)


@pytest.fixture(scope="module")
def module_offline_client(ipfs_is_available: bool):
	yield from _generate_client(ipfs_is_available, True)


@pytest.fixture
def cleanup_pins(client):
	pinned = set(client.pin.ls(type="recursive")["Keys"])
	
	yield
	
	for multihash in client.pin.ls(type="recursive")["Keys"]:
		if multihash not in pinned:
			client.pin.rm(multihash)


@pytest.fixture
def daemon():
	"""Result replaced by plugin in `run-tests.py` with the subprocess object of
	the spawned daemon."""
	return None
