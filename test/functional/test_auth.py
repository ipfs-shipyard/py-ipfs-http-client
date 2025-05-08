

def test_basic_auth(ipfs_service_client):
	"""
	Validate that client can connect to an IPFS api that is secured
	behind an HTTP reverse proxy requiring basic authentication.
	"""

	response = ipfs_service_client.version()

	# Matches version in test/functional/docker-compose.yml
	assert response['Version'] == '0.8.0'
