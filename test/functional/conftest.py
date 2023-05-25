# Note that this file is special in that py.test will automatically import this file and gather
# its list of fixtures even if it is not directly imported into the corresponding test case.

import os
import pathlib
import pytest
import sys
import typing as ty
from multiaddr import Multiaddr

import ipfshttpclient


TEST_DIR: pathlib.Path = pathlib.Path(__file__).parent


def _running_in_linux() -> bool:
	return sys.platform == 'linux'


def _running_in_travis_ci() -> bool:
	return '/home/travis/build' in os.getenv('PATH')


@pytest.fixture(scope='session')
def fake_dir() -> pathlib.Path:
	return TEST_DIR.joinpath('fake_dir')


@pytest.fixture(scope='session')
def docker_compose_file() -> str:
	"""
	Override the location of the file used by pytest-docker.

	The fixture name must be docker_compose_file and return str.
	"""

	if _running_in_travis_ci():
		pytest.skip('Docker hub reports rate limit errors on pulls from Travis CI servers')
	elif not _running_in_linux():
		pytest.skip("No IPFS server build for Windows; Travis doesn't support Docker on mac")

	return str(TEST_DIR.joinpath('docker-compose.yml'))


@pytest.fixture(scope='session')
def ipfs_service_address(docker_ip, docker_services, ipfs_service_auth) -> Multiaddr:
	port = docker_services.port_for('proxy', 80)
	address = Multiaddr(f'/ip4/{docker_ip}/tcp/{port}')

	print(f'Will connect to {address}')

	def is_responsive() -> bool:
		try:
			with ipfshttpclient.connect(address, auth=ipfs_service_auth):
				pass
		except ipfshttpclient.exceptions.Error:
			return False
		else:
			return True

	docker_services.wait_until_responsive(
		timeout=20,  # Pulling the docker image is not included in this timeout
		pause=0.5,
		check=is_responsive
	)

	return address


@pytest.fixture(scope='session')
def ipfs_service_auth() -> ty.Tuple[str, str]:
	return 'TheUser', 'ThePassword'


@pytest.fixture(scope="function")
def ipfs_service_client(ipfs_service_address, ipfs_service_auth):
	with ipfshttpclient.connect(
		addr=ipfs_service_address,
		auth=ipfs_service_auth
	) as client:
		yield client


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
