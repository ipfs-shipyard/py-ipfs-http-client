# _*_ coding: utf-8 -*-
import conftest


def test_new(client):
	expected_keys = {"Hash"}
	res = client.object.new()
	assert set(res.keys()).issuperset(expected_keys)


def test_stat(client):
	expected_keys = {"Hash", "CumulativeSize", "DataSize", "NumLinks", "LinksSize", "BlockSize"}
	resource = client.add_str("Mary had a little lamb")
	resp_stat = client.object.stat(resource)
	assert set(resp_stat.keys()).issuperset(expected_keys)


def test_put_get(client):
	# Set paths to test json files
	path_no_links = conftest.TEST_DIR / "fake_json" / "no_links.json"
	path_links = conftest.TEST_DIR / "fake_json" / "links.json"

	# Put the json objects on the DAG
	no_links = client.object.put(path_no_links)
	links = client.object.put(path_links)

	# Verify the correct content was put
	assert no_links["Hash"] == "QmXg9Pp2ytZ14xgmQjYEiHjVjMFXzCVVEcRTWJBmLgR39V"
	assert links["Hash"] == "QmZZmY4KCu9r3e7M2Pcn46Fc5qbn6NpzaAGaYb22kbfTqm"

	# Get the objects from the DAG
	get_no_links = client.object.get("QmXg9Pp2ytZ14xgmQjYEiHjVjMFXzCVVEcRTWJBmLgR39V")
	get_links = client.object.get("QmZZmY4KCu9r3e7M2Pcn46Fc5qbn6NpzaAGaYb22kbfTqm")

	# Verify the objects we put have been gotten
	assert get_no_links["Data"] == "abc"
	assert get_links["Data"] == "another"
	assert get_links["Links"][0]["Name"] == "some link"


def test_links(client):
	# Set paths to test json files
	path_links = conftest.TEST_DIR / "fake_json" / "links.json"

	# Put json object on the DAG and get its links
	client.object.put(path_links)
	links = client.object.links("QmZZmY4KCu9r3e7M2Pcn46Fc5qbn6NpzaAGaYb22kbfTqm")

	# Verify the correct link has been gotten
	assert links["Links"][0]["Hash"] == "QmXg9Pp2ytZ14xgmQjYEiHjVjMFXzCVVEcRTWJBmLgR39V"


def test_data(client):
	# Set paths to test json files
	path_links = conftest.TEST_DIR / "fake_json" / "links.json"

	# Put json objects on the DAG and get its data
	client.object.put(path_links)
	data = client.object.data("QmZZmY4KCu9r3e7M2Pcn46Fc5qbn6NpzaAGaYb22kbfTqm")

	# Verify the correct bytes have been gotten
	assert data == b"another"


def test_patch_append_data(client):
	"""Warning, this test depends on the contents of
		test/functional/fake_dir/fsdfgh
	"""
	result = client.object.patch.append_data(
		"QmdfTbBqBPQ7VNxZEYEj14VmRuZBkqFbiwReogJgS1zR1n",
		conftest.TEST_DIR / "fake_dir" / "fsdfgh"
	)
	assert result == {"Hash": "QmcUsyoGVxWoQgYKgmLaDBGm8J3eHWfchMh3oDUD5FrrtN"}


def test_patch_add_link(client):
	"""Warning, this test depends on the contents of
		test/functional/fake_dir/fsdfgh
	"""
	result = client.object.patch.add_link(
		"QmdfTbBqBPQ7VNxZEYEj14VmRuZBkqFbiwReogJgS1zR1n", "self",
		"QmdfTbBqBPQ7VNxZEYEj14VmRuZBkqFbiwReogJgS1zR1n"
	)
	assert result == {"Hash": "QmbWSr7YXBLcF23VVb7yPvUuogUPn46GD7gXftXC6mmsNM"}


def test_patch_rm_link(client):
	"""Warning, this test depends on the contents of
		test/functional/fake_dir/fsdfgh
	"""
	result = client.object.patch.rm_link(
		"QmbWSr7YXBLcF23VVb7yPvUuogUPn46GD7gXftXC6mmsNM", "self"
	)
	assert result == {"Hash": "QmdfTbBqBPQ7VNxZEYEj14VmRuZBkqFbiwReogJgS1zR1n"}


def test_patch_set_data(client):
	"""Warning, this test depends on the contents of
		test/functional/fake_dir/popoiopiu
	"""
	result = client.object.patch.set_data(
		"QmdfTbBqBPQ7VNxZEYEj14VmRuZBkqFbiwReogJgS1zR1n",
		conftest.TEST_DIR / "fake_dir" / "popoiopiu"
	)
	assert result == {"Hash": "QmV4QR7MCBj5VTi6ddHmXPyjWGzbaKEtX2mx7axA5PA13G"}