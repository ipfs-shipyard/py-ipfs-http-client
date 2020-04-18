import time

import pytest



def test_version(client):
	expected_keys = {"Repo", "Commit", "Version"}
	resp_version = client.version()
	assert set(resp_version.keys()).issuperset(expected_keys)


def test_id(client):
	expected_keys = {"PublicKey", "ProtocolVersion", "ID", "AgentVersion", "Addresses"}
	resp_id = client.id()
	assert set(resp_id.keys()).issuperset(expected_keys)


#################
# Shutdown test #
#################

@pytest.mark.last
def test_daemon_stop(daemon, client):
	# The value for the `daemon` “fixture” is injected using a pytest plugin
	# with access to the created daemon subprocess object defined directly
	# in the `test/run-test.py` file
	if not daemon:
		pytest.skip("Not started using `test/run-test.py`")
	
	def daemon_is_running():
		return daemon.poll() is None
	
	# Daemon should still be running at this point
	assert daemon_is_running()
	
	# Send stop request
	client.stop()
	
	# Wait for daemon process to disappear
	for _ in range(10000):
		if not daemon_is_running():
			break
		time.sleep(0.001)
	
	# Daemon should not be running anymore
	assert not daemon_is_running()
