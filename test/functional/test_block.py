# _*_ coding: utf-8 -*-
import conftest


TEST_MULTIHASH    = "QmYA2fn8cMbVWo4v95RwcwJVyQsNtnEwHerfWR8UNtEwoE"
TEST_CONTENT_SIZE = 248

TEST_PUT_FILEPATH  = conftest.TEST_DIR / "fake_dir" / "fsdfgh"
TEST_PUT_MULTIHASH = "QmPevo2B1pwvDyuZyJbWVfhwkaGPee3f1kX36wFmqx1yna"


# Uncomment this if you don't want to wait for the `test_start` test during development:
#import pytest
#pytest.skip("TEMP!", allow_module_level=True)


def test_stat(client):
	expected_keys = {"Key", "Size"}
	res = client.block.stat(TEST_MULTIHASH)
	assert set(res.keys()).issuperset(expected_keys)


def test_get(client):
	assert len(client.block.get(TEST_MULTIHASH)) == TEST_CONTENT_SIZE


def test_put(client):
	expected_keys = {"Key", "Size"}
	res = client.block.put(TEST_PUT_FILEPATH)
	assert set(res.keys()).issuperset(expected_keys)
	assert res["Key"] == TEST_PUT_MULTIHASH