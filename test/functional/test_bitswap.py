# _*_ coding: utf-8 -*-


def test_wantlist(client):
	result = client.bitswap.wantlist(peer="QmdkJZUWnVkEc6yfptVu4LWY8nHkEnGwsxqQ233QSGj8UP")
	assert type(result) is dict
	assert "Keys" in result


def test_stat(client):
	result = client.bitswap.stat()
	assert type(result) is dict
	assert "Wantlist" in result


def test_unwant(client):
	"""
	Cannot ensure what is present in the wantlist prior to execution, so just ensure
	something comes back.
	"""
	result = client.bitswap.unwant(key="QmZTR5bcpQD7cFgTorqxZDYaew1Wqgfbd2ud9QqGPAkK2V")
	assert result is not None