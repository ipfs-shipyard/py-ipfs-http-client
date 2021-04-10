

def test_version(client):
	expected_keys = {"Repo", "Commit", "Version"}
	resp_version = client.version()
	assert set(resp_version.keys()).issuperset(expected_keys)


def test_id(client):
	expected_keys = {"PublicKey", "ProtocolVersion", "ID", "AgentVersion", "Addresses"}
	resp_id = client.id()
	assert set(resp_id.keys()).issuperset(expected_keys)
