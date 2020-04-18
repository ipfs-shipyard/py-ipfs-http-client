import cid
import io
import pytest

import conftest

TEST1_FILEPATH = conftest.TEST_DIR / "fake_dir" / "fsdfgh"
TEST1_CID_STR  = "QmPevo2B1pwvDyuZyJbWVfhwkaGPee3f1kX36wFmqx1yna"
TEST1_SIZE     = 8

TEST2_CONTENT = b"Hello World!"
TEST2_CID_STR = "bafkreid7qoywk77r7rj3slobqfekdvs57qwuwh5d2z3sqsw52iabe3mqne"
TEST2_CID_OBJ = cid.make_cid(TEST2_CID_STR)
TEST2_SIZE    = len(TEST2_CONTENT)


@pytest.mark.dependency()
def test_put(client):
	expected_keys = {"Key", "Size"}
	res = client.block.put(TEST1_FILEPATH)
	assert set(res.keys()).issuperset(expected_keys)
	assert res["Key"] == TEST1_CID_STR


@pytest.mark.dependency(depends=["test_put"])
def test_stat(client):
	expected_keys = {"Key", "Size"}
	res = client.block.stat(TEST1_CID_STR)
	assert set(res.keys()).issuperset(expected_keys)


@pytest.mark.dependency(depends=["test_put"])
def test_get(client):
	assert len(client.block.get(TEST1_CID_STR)) == TEST1_SIZE


@pytest.mark.dependency()
def test_put_str(client):
	expected_keys = {"Key", "Size"}
	res = client.block.put(io.BytesIO(TEST2_CONTENT), opts={"format": "raw"})
	assert set(res.keys()).issuperset(expected_keys)
	assert res["Key"] == TEST2_CID_STR


@pytest.mark.dependency(depends=["test_put_str"])
def test_stat_cid_obj(client):
	assert len(client.block.get(TEST2_CID_OBJ)) == TEST2_SIZE