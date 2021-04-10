# Note that this file is special in that py.test will automatically import this file and gather
# its list of fixtures even if it is not directly imported into the corresponding test case.

import pathlib
import pytest

from multiaddr import Multiaddr

import ipfshttpclient


TEST_DIR: pathlib.Path = pathlib.Path(__file__).parent


@pytest.fixture(scope='session')
def docker_compose_file() -> str:
	"""
	Override the location of the file used by pytest-docker.

	The fixture name must be docker_compose_file and return str.
	"""

	return str(TEST_DIR.joinpath('docker-compose.yml'))


@pytest.fixture(scope='session')
def ipfs_service_address(docker_ip, docker_services) -> Multiaddr:
	port = docker_services.port_for('ipfs', 5001)
	address = Multiaddr(f'/ip4/{docker_ip}/tcp/{port}')

	print(f'Will connect to {address}')

	def is_responsive() -> bool:
		try:
			with ipfshttpclient.connect():
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
def fake_dir() -> pathlib.Path:
	return TEST_DIR.joinpath('fake_dir')


def sort_by_key(items, key="Name"):
	return sorted(items, key=lambda x: x[key])


@pytest.fixture(scope="function")
def client(ipfs_service_address):
	with ipfshttpclient.connect(addr=ipfs_service_address, offline=False) as client:
		yield client


@pytest.fixture(scope="function")
def offline_client(ipfs_service_address):
	with ipfshttpclient.connect(addr=ipfs_service_address, offline=True) as client:
		yield client


@pytest.fixture(scope="module")
def module_offline_client(ipfs_service_address):
	with ipfshttpclient.connect(addr=ipfs_service_address, offline=True) as client:
		yield client


@pytest.fixture
def cleanup_pins(client):
	pinned = set(client.pin.ls(type="recursive")["Keys"])
	
	yield
	
	for multihash in client.pin.ls(type="recursive")["Keys"]:
		if multihash not in pinned:
			client.pin.rm(multihash)
