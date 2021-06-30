
import base64
import ipfshttpclient
import json
import pytest

from ipaddress import ip_address, IPv4Address, IPv6Address
from ipfshttpclient.exceptions import StatusError
from multiaddr import Multiaddr
from _pytest.fixtures import FixtureRequest
from pytest_localserver.http import ContentServer
from urllib.parse import urlparse
from werkzeug import Request, Response


BASIC_USERNAME = 'basic_username'
BASIC_PASSWORD = 'basic_password'


def _basic_auth_token(username: str, password: str) -> str:
	return base64.b64encode(f'{username}:{password}'.encode('utf-8')).decode('utf-8')


def _url_to_multiaddr(url: str) -> Multiaddr:
	parsed = urlparse(url)

	try:
		ip = ip_address(parsed.hostname)
	except ValueError:
		ip = None

	if ip is None:
		prefix = '/dns'
	elif isinstance(ip, IPv4Address):
		prefix = '/ip4'
	elif isinstance(ip, IPv6Address):
		prefix = '/ip6'
	else:
		raise TypeError(f"Don't know how to convert {ip} to a {Multiaddr.__name__}")

	return Multiaddr(f'{prefix}/{parsed.hostname}/tcp/{parsed.port}/{parsed.scheme}')


class AuthenticatingServer(ContentServer):
	@staticmethod
	def _is_authorized(expected_credentials: str, request: Request) -> bool:
		authorizations = request.headers.get_all('Authorization')

		if authorizations and len(authorizations) == 1:
			authorization = authorizations[0]

			return authorization == f'Basic {expected_credentials}'
		else:
			return False

	def __call__(self, environ, start_response) -> Response:
		request = Request(environ)
		self.requests.append(request)

		expected_credentials = _basic_auth_token(BASIC_USERNAME, BASIC_PASSWORD)

		if self._is_authorized(expected_credentials, request):
			response = Response(status=self.code)
			response.headers.clear()
			response.headers.extend(self.headers)

			response.data = self.content
		else:
			response = Response(status=401)
			response.headers.clear()
			response.data = 'Unauthorized'

		return response(environ, start_response)


@pytest.fixture(scope='module')
def authenticating_server(request: FixtureRequest) -> ContentServer:
	server = AuthenticatingServer()
	server.start()
	request.addfinalizer(server.stop)

	return server


def test_basic_auth_failure(authenticating_server: ContentServer) -> None:
	headers = {
		'Content-Type': 'text/json'
	}

	version = '0.0.1'

	response = {
		'Version': version
	}

	authenticating_server.serve_content(json.dumps(response), headers=headers)

	address = _url_to_multiaddr(authenticating_server.url)

	with pytest.raises(StatusError) as failure:
		ipfshttpclient.connect(
			addr=address,
			auth=('wrong', 'wrong')
		)

	assert failure.value.status_code == 401


def test_basic_auth_success(authenticating_server: ContentServer) -> None:
	headers = {
		'Content-Type': 'text/json'
	}

	version = '0.0.1'

	response = {
		'Version': version
	}

	authenticating_server.serve_content(json.dumps(response), headers=headers)

	address = _url_to_multiaddr(authenticating_server.url)

	with ipfshttpclient.connect(
		addr=address,
		auth=(BASIC_USERNAME, BASIC_PASSWORD)
	) as client:
		assert client.version()['Version'] == version
