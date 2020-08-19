import io
import pytest


def test_export(client):
    assert 0


def test_import_(client):
    assert 0


def test_put_get(client):
    data = io.BytesIO(br'{"links": []}')
    response = client.dag.put(data)

    assert 'Cid' in response
    assert '/' in response['Cid']
    assert response['Cid']['/'] == 'bafyreidepjmjhvhlvp5eyxqpmyyi7rxwvl7wsglwai3cnvq63komq4tdya'

    response = client.dag.get('bafyreidepjmjhvhlvp5eyxqpmyyi7rxwvl7wsglwai3cnvq63komq4tdya')

    assert 'links' in response
    assert response['links'] == []


def test_resolve(client):
    assert 0
