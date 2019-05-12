# _*_ coding: utf-8 -*-
import ipfshttpclient

import conftest


def test_ipfs_node_available():
	"""
	Dummy test to ensure that running the tests without a daemon produces a failure, since we
	think it's unlikely that people running tests want this
	"""
	assert conftest.is_available(), \
	       "Functional tests require an IPFS node to be available at: {0}" \
	       .format(ipfshttpclient.DEFAULT_ADDR)


def test_add_json(client, cleanup_pins):
	data = {"Action": "Open", "Type": "PR", "Name": "IPFS", "Pubkey": 7}
	res = client.add_json(data)

	assert data == client.get_json(res)

	# have to test the string added to IPFS, deserializing JSON will not
	# test order of keys
	assert '{"Action":"Open","Name":"IPFS","Pubkey":7,"Type":"PR"}' == client.cat(res).decode("utf-8")