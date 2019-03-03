# _*_ coding: utf-8 -*-

import pytest


def get_key(client, key_name):
	keys = client.key.list()["Keys"]
	for k in keys:
		if k["Name"] == key_name:
			return k
	raise Exception("Unknown key: %s" % key_name)


def hash_to_path(ns, h):
	assert "/" not in h
	assert h == h.strip()
	return "/" + ns + "/" + h


def hash_to_ipfs_path(h):
	return hash_to_path("ipfs", h)


def hash_to_ipns_path(h):
	return hash_to_path("ipns", h)


class Resources(object):
	def __init__(self, offline_client):
		self.client = offline_client


	def __enter__(self):
		self.key_self = get_key(self.client, "self")
		self.key_test1 = self.client.key.gen("ipfshttpclient-test-name-1", "rsa")
		self.key_test2 = self.client.key.gen("ipfshttpclient-test-name-2", "rsa")
		self.msg1 = hash_to_ipfs_path(self.client.add_str("Mary had a little lamb"))
		self.msg2 = hash_to_ipfs_path(self.client.add_str("Mary had a little alpaca"))
		self.msg3 = hash_to_ipfs_path(self.client.add_str("Mary had a little goat"))
		return self


	def __exit__(self, t, v, tb):
		self.client.pin.rm(self.msg1, self.msg2, self.msg3)
		self.client.key.rm(self.key_test1["Name"], self.key_test2["Name"])


class PublishedMapping(object):
	def __init__(self, name, path):
		self.name = name
		self.path = path


@pytest.fixture(scope="module")
def resources(module_offline_client):
	with Resources(module_offline_client) as resources:
		yield resources


@pytest.fixture(scope="module")
def published_mapping(module_offline_client, resources):
	# we're not testing publish here, pass whatever args we want
	resp = module_offline_client.name.publish(
		resources.msg3,
		key=resources.key_test2["Name"], resolve=False,
		lifetime="5m", ttl="5m", allow_offline=True)
	return PublishedMapping(resp["Name"], resp["Value"])


def check_resolve(resp, path):
	assert resp["Path"] == path


def check_publish(offline_client, response_path, resolved_path, key, resp):

	name = resp["Name"]
	assert name == key["Id"]
	assert resp["Value"] == response_path

	# we're not testing resolve here, pass whatever args we want
	resolve_resp = offline_client.name.resolve(
		name,
		recursive=True, dht_record_count=0, dht_timeout="1s",
		offline=True)
	check_resolve(resolve_resp, resolved_path)


def test_publish_self(offline_client, resources):
	resp = offline_client.name.publish(resources.msg1, allow_offline=True)
	check_publish(offline_client, resources.msg1, resources.msg1,
	              resources.key_self, resp)


def test_publish_params(offline_client, resources):
	resp = offline_client.name.publish(resources.msg1,
	                                   lifetime="25h", ttl="1m",
	                                   allow_offline=True)
	check_publish(offline_client, resources.msg1, resources.msg1,
	              resources.key_self, resp)


def test_publish_key(offline_client, resources):
	resp = offline_client.name.publish(
		resources.msg2,
		key=resources.key_test1["Name"], allow_offline=True)
	check_publish(offline_client, resources.msg2, resources.msg2,
	              resources.key_test1, resp)


def test_publish_indirect(offline_client, resources, published_mapping):
	path = hash_to_ipns_path(published_mapping.name)
	resp = offline_client.name.publish(path,
	                                   resolve=True, allow_offline=True)
	check_publish(offline_client, path, published_mapping.path,
	              resources.key_self, resp)


def test_resolve(offline_client, published_mapping):
	check_resolve(offline_client.name.resolve(published_mapping.name),
	              published_mapping.path)


def test_resolve_recursive(offline_client, published_mapping):
	inner_path = hash_to_ipns_path(published_mapping.name)
	res = offline_client.name.publish(inner_path,
	                                  resolve=False, allow_offline=True)
	outer_path = res["Name"]

	resp = offline_client.name.resolve(outer_path, recursive=True)
	check_resolve(resp, published_mapping.path)


def test_resolve_params(offline_client, published_mapping):
	resp = offline_client.name.resolve(
		published_mapping.name,
		nocache=True, dht_record_count=1, dht_timeout="180s",
		offline=True)
	check_resolve(resp, published_mapping.path)
