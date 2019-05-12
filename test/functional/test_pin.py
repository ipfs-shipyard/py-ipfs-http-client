# _*_ coding: utf-8 -*-
import pytest

import ipfshttpclient.exceptions


class Resources(object):
	def __init__(self, client):
		self.msg = client.add_str("Mary had a little lamb")
		self.msg2 = client.add_str("Mary had a little alpaca")
		resp_add = client.add("test/functional/fake_dir", recursive=True)
		self.fake_dir_hashes = [el["Hash"] for el in resp_add if "Hash" in el]
		for resp in resp_add:
			if resp["Name"] == "fake_dir":
				self.fake_dir_hash = resp["Hash"]
			elif resp["Name"] == "fake_dir/test2":
				self.fake_dir_test2_hash = resp["Hash"]

@pytest.fixture  # noqa
def resources(client):
	return Resources(client)


def is_pinned(client, path):
	error_msg = None
	try:
		resp = client.pin.ls(path)
		assert path.split("/")[-1] in resp["Keys"]
	except ipfshttpclient.exceptions.ErrorResponse as exc:
		error_msg = exc.args[0]
		if "not pinned" in error_msg:
			return False
		raise
	return True


def test_ls_void(client, resources):
	pins = client.pin.ls()["Keys"]
	assert len(pins) >= 2
	assert resources.msg in pins
	assert resources.msg2 in pins


def test_ls_single(client, resources):
	pins = client.pin.ls(resources.msg)["Keys"]
	assert len(pins) == 1
	assert resources.msg in pins


def test_ls_multiple(client, resources):
	pins = client.pin.ls(resources.msg, resources.msg2)["Keys"]
	assert len(pins) == 2
	assert resources.msg in pins
	assert resources.msg2 in pins


def test_ls_add_rm_single(client, resources):
	# Get pinned objects at start.
	pins_begin = client.pin.ls()["Keys"]

	# Unpin the resource if already pinned.
	if resources.msg in pins_begin.keys():
		client.pin.rm(resources.msg)

	# No matter what, the resource should not be pinned at this point
	assert resources.msg not in client.pin.ls()["Keys"]
	assert not is_pinned(client, resources.msg)

	for option in (True, False):
		# Pin the resource.
		resp_add = client.pin.add(resources.msg, recursive=option)
		pins_afer_add = client.pin.ls()["Keys"]
		assert resp_add["Pins"] == [resources.msg]
		assert resources.msg in pins_afer_add
		if option:
			assert pins_afer_add[resources.msg]["Type"] == "recursive"
		else:
			assert pins_afer_add[resources.msg]["Type"] != "recursive"

		# Unpin the resource
		resp_rm = client.pin.rm(resources.msg)
		pins_afer_rm = client.pin.ls()["Keys"]
		assert resp_rm["Pins"] == [resources.msg]
		assert resources.msg not in pins_afer_rm

	# Get pinned objects at end
	pins_end = client.pin.ls()["Keys"]

	# Compare pinned items from start to finish of test
	assert resources.msg not in pins_end.keys()
	assert not is_pinned(client, resources.msg)


def test_ls_add_rm_directory(client, resources):
	# Remove fake_dir if it had previously been pinned
	if resources.fake_dir_hash in client.pin.ls(type="recursive")["Keys"].keys():
		client.pin.rm(resources.fake_dir_hash)

	# Make sure I removed it
	assert resources.fake_dir_hash not in client.pin.ls()["Keys"].keys()

	# Add "fake_dir" recursively
	client.pin.add(resources.fake_dir_hash)

	# Make sure all appear on the list of pinned objects
	pins_after_add = client.pin.ls()["Keys"].keys()
	assert set(pins_after_add).issuperset(set(resources.fake_dir_hashes))

	# Clean up
	client.pin.rm(resources.fake_dir_hash)
	pins_end = client.pin.ls(type="recursive")["Keys"].keys()
	assert resources.fake_dir_hash not in pins_end


def test_add_update_verify_rm(client, resources):
	# Get pinned objects at start
	pins_begin = client.pin.ls(type="recursive")["Keys"].keys()

	# Remove fake_dir and demo resource if it had previously been pinned
	if resources.fake_dir_hash in pins_begin:
		client.pin.rm(resources.fake_dir_hash)
	if resources.fake_dir_test2_hash in pins_begin:
		client.pin.rm(resources.fake_dir_test2_hash)

	# Ensure that none of the above are pinned anymore
	pins_after_rm = client.pin.ls(type="recursive")["Keys"].keys()
	assert resources.fake_dir_hash       not in pins_after_rm
	assert resources.fake_dir_test2_hash not in pins_after_rm

	# Add pin for sub-directory
	client.pin.add(resources.fake_dir_test2_hash)

	# Replace it by pin for the entire fake dir
	client.pin.update(resources.fake_dir_test2_hash, resources.fake_dir_hash)

	# Ensure that the sub-directory is not pinned directly anymore
	pins_after_update = client.pin.ls(type="recursive")["Keys"].keys()
	assert resources.fake_dir_test2_hash not in pins_after_update
	assert resources.fake_dir_hash           in pins_after_update

	# Now add a pin to the sub-directory from the parent directory
	client.pin.update(resources.fake_dir_hash, resources.fake_dir_test2_hash, unpin=False)

	# Check integrity of all directory content hashes and whether all
	# directory contents have been processed in doing this
	hashes = []
	for result in client.pin.verify(resources.fake_dir_hash, verbose=True):
		assert result["Ok"]
		hashes.append(result["Cid"])
	assert resources.fake_dir_hash in hashes

	# Ensure that both directories are now recursively pinned
	pins_after_update2 = client.pin.ls(type="recursive")["Keys"].keys()
	assert resources.fake_dir_test2_hash in pins_after_update2
	assert resources.fake_dir_hash       in pins_after_update2

	# Clean up
	client.pin.rm(resources.fake_dir_hash, resources.fake_dir_test2_hash)