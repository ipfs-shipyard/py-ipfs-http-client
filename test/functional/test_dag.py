import io

import pytest

import conftest


def test_put_get_resolve(client):
	version = tuple(map(int, client.version()["Version"].split('-', 1)[0].split('.')))
	if version < (0, 5):
		pytest.skip("IPFS DAG APIs first appeared in go-IPFS 0.5")

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
	version = tuple(map(int, client.version()["Version"].split('-', 1)[0].split('.')))
	if version < (0, 5):
		pytest.skip("IPFS DAG APIs first appeared in go-IPFS 0.5")

	# This file was created by inserting a simple JSON object into IPFS and
	# exporting it using `ipfs dag export <cid> > file.car`
	data_car = conftest.TEST_DIR / 'fake_json' / 'data.car'
	data_car = str(data_car)  #PY35

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
