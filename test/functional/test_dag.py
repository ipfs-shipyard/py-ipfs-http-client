import io

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


def test_import_export(client):
	data_car = conftest.TEST_DIR / 'fake_json' / 'data.car'
	with open(data_car, 'rb') as file:
		response = client.dag.imprt(file)

	assert 'Root' in response
	assert 'Cid' in response['Root']
	assert '/' in response['Root']['Cid']

	cid = response['Root']['Cid']
	assert cid['/'] == 'bafyreidepjmjhvhlvp5eyxqpmyyi7rxwvl7wsglwai3cnvq63komq4tdya'

	data = client.dag.export('bafyreidepjmjhvhlvp5eyxqpmyyi7rxwvl7wsglwai3cnvq63komq4tdya')

	with open(data_car, 'rb') as file:
		assert data == file.read()
