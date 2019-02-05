# _*_ coding: utf-8 -*-
try:
	import cid
except ImportError:
	cid = None
import pytest

import conftest


TEST_CID_STR      = "QmYA2fn8cMbVWo4v95RwcwJVyQsNtnEwHerfWR8UNtEwoE"
TEST_CONTENT_SIZE = 248

if cid:
	TEST2_CID_OBJ      = cid.make_cid("zb2rhmDGuPfTrMTyrvN6MWx1tbZ7RdVJgC16T8iY7Ff6Gm775")
	TEST2_CONTENT_SIZE = 11

TEST_PUT_FILEPATH = conftest.TEST_DIR / "fake_dir" / "fsdfgh"
TEST_PUT_CID      = "QmPevo2B1pwvDyuZyJbWVfhwkaGPee3f1kX36wFmqx1yna"


# Uncomment this if you don't want to wait for the `test_start` test during development:
#import pytest
#pytest.skip("TEMP!", allow_module_level=True)


def test_stat(client):
	expected_keys = {"Key", "Size"}
	res = client.block.stat(TEST_CID_STR)
	assert set(res.keys()).issuperset(expected_keys)


def test_get(client):
	assert len(client.block.get(TEST_CID_STR)) == TEST_CONTENT_SIZE


@pytest.mark.skipif(not cid, reason="requires py-cid (Python 3.5+ only)")
def test_stat_cid_obj(client):
	assert len(client.block.get(TEST2_CID_OBJ)) == TEST2_CONTENT_SIZE


def test_put(client):
	expected_keys = {"Key", "Size"}
	res = client.block.put(TEST_PUT_FILEPATH)
	assert set(res.keys()).issuperset(expected_keys)
	assert res["Key"] == TEST_PUT_CID