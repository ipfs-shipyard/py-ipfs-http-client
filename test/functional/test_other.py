

def test_add_json(client, cleanup_pins):
	data = {"Action": "Open", "Type": "PR", "Name": "IPFS", "Pubkey": 7}
	res = client.add_json(data)

	assert data == client.get_json(res)

	# have to test the string added to IPFS, deserializing JSON will not
	# test order of keys
	assert '{"Action":"Open","Name":"IPFS","Pubkey":7,"Type":"PR"}' == client.cat(res).decode("utf-8")
