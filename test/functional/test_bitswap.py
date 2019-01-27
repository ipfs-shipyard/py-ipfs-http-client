# _*_ coding: utf-8 -*-


def test_wantlist(client):
	result = client.bitswap.wantlist(peer="QmdkJZUWnVkEc6yfptVu4LWY8nHkEnGwsxqQ233QSGj8UP")
	assert type(result) is dict
	assert "Keys" in result


def test_stat(client):
	result = client.bitswap.stat()
	assert type(result) is dict
	assert "Wantlist" in result