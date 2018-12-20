# _*_ coding: utf-8 -*-
import conftest


##################
# Daemon Logging #
##################

def test_log_ls_level(client):
	"""
	Unfortunately there is no way of knowing the logging levels prior
	to this test. This makes it impossible to guarantee that the logging
	levels are the same as before the test was run.
	"""
	# Retrieves the list of logging subsystems for a running daemon.
	resp_ls = client.unstable.log.ls()
	# The response should be a dictionary with only one key ('Strings').
	assert "Strings" in resp_ls
	
	# Sets the logging level to 'error' for the first subsystem found.
	sub = resp_ls["Strings"][0]
	resp_level = client.unstable.log.level(sub, "error")
	assert resp_level["Message"] == "Changed log level of '{0}' to 'error'\n".format(sub)


def test_log_tail(client):
	# Gets the response object.
	tail = client.unstable.log.tail()
	
	# The log should have been parsed into a dictionary object with
	# various keys depending on the event that occured.
	assert type(next(tail)) is dict


############
# Refs API #
############

REFS_RESULT = [
	{"Err": "", "Ref": "QmQcCtMgLVwvMQGu6mvsRYLjwqrZJcYtH4mboM9urWW9vX"},
	{"Err": "", "Ref": "QmYAhvKYu46rh5NcHzeu6Bhc7NG9SqkF9wySj2jvB74Rkv"},
	{"Err": "", "Ref": "QmStL6TPbJfMHQhHjoVT93kCynVx3GwLf7xwgrtScqABhU"},
	{"Err": "", "Ref": "QmRphRr6ULDEj7YnXpLdnxhnPiVjv5RDtGX3er94Ec6v4Q"}
]


def test_refs_local_1(client):
	with open(str(conftest.TEST_DIR / "fake_dir" / "fsdfgh"), "rb") as fp:
		res = client.add(fp, pin=False)
		
		assert res["Hash"] == "QmQcCtMgLVwvMQGu6mvsRYLjwqrZJcYtH4mboM9urWW9vX"
		
		assert res["Hash"] not in client.pin.ls(type="recursive")
		assert res["Hash"]     in list(map(lambda i: i["Ref"], client.unstable.refs.local()))


def test_refs_local_2(client):
	res = client.add(conftest.TEST_DIR / "fake_dir" / "fsdfgh", pin=False)
	
	assert res["Hash"] == "QmQcCtMgLVwvMQGu6mvsRYLjwqrZJcYtH4mboM9urWW9vX"
	
	assert res["Hash"] not in client.pin.ls(type="recursive")
	assert res["Hash"]     in list(map(lambda i: i["Ref"], client.unstable.refs.local()))


def test_refs(client, cleanup_pins):
	client.add(conftest.TEST_DIR / "fake_dir", recursive=True)
	
	refs = client.unstable.refs("QmNx8xVu9mpdz9k6etbh2S8JwZygatsZVCH4XhgtfUYAJi")
	assert conftest.sort_by_key(REFS_RESULT, "Ref") == conftest.sort_by_key(refs, "Ref")