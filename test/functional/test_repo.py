# _*_ coding: utf-8 -*-


def test_stat(client):
	# Verify that the correct key-value pairs are returned
	stat = client.repo.stat()
	assert sorted(stat.keys()) == [
		u"NumObjects", u"RepoPath", u"RepoSize",
		u"StorageMax", u"Version"
	]


def test_gc(client):
	# Add and unpin an object to be garbage collected
	garbage = client.add_str("Test String")
	client.pin.rm(garbage)
	
	# Collect the garbage object with object count before and after
	orig_objs = client.repo.stat()["NumObjects"]
	gc = client.repo.gc()
	cur_objs = client.repo.stat()["NumObjects"]
	
	# Verify the garbage object was collected
	assert orig_objs > cur_objs
	keys = [el["Key"]["/"] for el in gc]
	assert garbage in keys


def test_gc_no_result(client):
	# Add and unpin an object to be garbage collected
	garbage = client.add_str("Test String")
	client.pin.rm(garbage)

	# Collect the garbage object with object count before and after
	orig_objs = client.repo.stat()["NumObjects"]
	gc = client.repo.gc(return_result=False)
	cur_objs = client.repo.stat()["NumObjects"]

	# Verify the garbage object was collected
	assert orig_objs > cur_objs
	assert gc is None
