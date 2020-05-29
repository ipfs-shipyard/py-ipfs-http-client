def test_wantlist(client):
	result = client.bitswap.wantlist(peer="QmdkJZUWnVkEc6yfptVu4LWY8nHkEnGwsxqQ233QSGj8UP")
	assert "Keys" in result


def test_stat(client):
	result = client.bitswap.stat()
	assert "Wantlist" in result