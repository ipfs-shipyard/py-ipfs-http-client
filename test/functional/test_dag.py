import io
import pytest

import conftest

def test_put_get_resolve(client):
	data = io.BytesIO(br'{"links": []}')
	response = client.dag.put(data)

	assert 'Cid' in response
	assert '/' in response['Cid']
	assert response['Cid']['/'] == 'bafyreidepjmjhvhlvp5eyxqpmyyi7rxwvl7wsglwai3cnvq63komq4tdya'

	response = client.dag.get('bafyreidepjmjhvhlvp5eyxqpmyyi7rxwvl7wsglwai3cnvq63komq4tdya')

	assert 'links' in response
	assert response['links'] == []

	response = client.dag.resolve('bafyreidepjmjhvhlvp5eyxqpmyyi7rxwvl7wsglwai3cnvq63komq4tdya')

	assert 'Cid' in response
	assert response['Cid']['/'] == 'bafyreidepjmjhvhlvp5eyxqpmyyi7rxwvl7wsglwai3cnvq63komq4tdya'

