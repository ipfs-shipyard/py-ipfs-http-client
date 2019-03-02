# _*_ coding: utf-8 -*-
try:
	import cid
except ImportError:
	cid = None
import io
import pytest

import conftest

TEST1_FILEPATH = conftest.TEST_DIR / "fake_dir" / "fsdfgh"
TEST1_CID_STR  = "QmPevo2B1pwvDyuZyJbWVfhwkaGPee3f1kX36wFmqx1yna"
TEST1_SIZE     = 8

TEST2_CONTENT = b"Hello World!"
TEST2_CID_STR = "zb2rhfE3SX3q7Ha6UErfMqQReKsmLn73BvdDRagHDM6X1eRFN"
TEST2_CID_OBJ = cid.make_cid(TEST2_CID_STR) if cid else None
TEST2_SIZE    = len(TEST2_CONTENT)


# Uncomment this if you don't want to wait for the `test_start` test during development:
#import pytest
#pytest.skip("TEMP!", allow_module_level=True)


def test_put(client):
	expected_keys = {"Key", "Size"}
	res = client.block.put(TEST1_FILEPATH)
	assert set(res.keys()).issuperset(expected_keys)
	assert res["Key"] == TEST1_CID_STR


@pytest.mark.run(after="test_put")
def test_stat(client):
	expected_keys = {"Key", "Size"}
	res = client.block.stat(TEST1_CID_STR)
	assert set(res.keys()).issuperset(expected_keys)


@pytest.mark.run(after="test_put")
def test_get(client):
	assert len(client.block.get(TEST1_CID_STR)) == TEST1_SIZE


def test_put_str(client):
	expected_keys = {"Key", "Size"}
	res = client.block.put(io.BytesIO(TEST2_CONTENT), opts={"format": "raw"})
	assert set(res.keys()).issuperset(expected_keys)
	assert res["Key"] == TEST2_CID_STR


@pytest.mark.skipif(not cid, reason="requires py-cid (Python 3.5+ only)")
@pytest.mark.run(after="test_put_str")
def test_stat_cid_obj(client):
	assert len(client.block.get(TEST2_CID_OBJ)) == TEST2_SIZE