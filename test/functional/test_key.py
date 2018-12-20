# _*_ coding: utf-8 -*-


def test_add_list_rename_rm(client):
	# Remove keys if they already exist
	key_list = list(map(lambda k: k["Name"], client.key.list()["Keys"]))
	if "ipfshttpclient-test-rsa" in key_list:
		client.key.rm("ipfshttpclient-test-rsa")
	if "ipfshttpclient-test-ed" in key_list:
		client.key.rm("ipfshttpclient-test-ed")

	# Add new RSA and ED25519 key
	key1 = client.key.gen("ipfshttpclient-test-rsa", "rsa")["Name"]
	key2 = client.key.gen("ipfshttpclient-test-ed", "ed25519")["Name"]

	# Validate the keys exist now
	key_list = list(map(lambda k: k["Name"], client.key.list()["Keys"]))
	assert key1 in key_list
	assert key2 in key_list

	# Rename the EC key
	key2_new = client.key.rename(key2, "ipfshttpclient-test-ed2")["Now"]

	# Validate that the key was successfully renamed
	key_list = list(map(lambda k: k["Name"], client.key.list()["Keys"]))
	assert key1     in key_list
	assert key2 not in key_list
	assert key2_new in key_list

	# Drop both keys with one request
	client.key.rm(key1, key2_new)

	# Validate that the keys are gone again
	key_list = list(map(lambda k: k["Name"], client.key.list()["Keys"]))
	assert key1     not in key_list
	assert key2_new not in key_list