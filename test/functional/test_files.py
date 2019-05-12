# _*_ coding: utf-8 -*-
import os
import shutil

import pytest

import ipfshttpclient.exceptions

import conftest



### test_add_multiple_from_list
FAKE_FILE1_PATH = conftest.TEST_DIR / "fake_dir" / "fsdfgh"
FAKE_FILE2_PATH = conftest.TEST_DIR / "fake_dir" / "popoiopiu"

FAKE_FILE1_HASH = {"Hash": "QmQcCtMgLVwvMQGu6mvsRYLjwqrZJcYtH4mboM9urWW9vX",
                   "Name": "fsdfgh", "Size": "16"}
FAKE_FILE1_RAW_LEAVES_HASH = {
	"Hash": "zb2rhXxZH5PFgCwBAm7xQMoBa6QWqytN8NPvXK7Qc9McDz9zJ",
	"Name": "fsdfgh", "Size": "8"
}

FAKE_FILE1_DIR_HASH = [
	{"Hash": "QmQcCtMgLVwvMQGu6mvsRYLjwqrZJcYtH4mboM9urWW9vX",
	 "Name": "fsdfgh", "Size": "16"},
	{"Hash": "Qme7vmxd4LAAYL7vpho3suQeT3gvMeLLtPdp7myCb9Db55",
	 "Name": "",       "Size": "68"}
]

FAKE_FILES_HASH = [
	{"Hash": "QmQcCtMgLVwvMQGu6mvsRYLjwqrZJcYtH4mboM9urWW9vX",
	 "Name": "fsdfgh",    "Size": "16"},
	{"Hash": "QmYAhvKYu46rh5NcHzeu6Bhc7NG9SqkF9wySj2jvB74Rkv",
	 "Name": "popoiopiu", "Size": "23"}
]

### test_add_multiple_from_dirname
FAKE_DIR_TEST2_PATH = conftest.TEST_DIR / "fake_dir" / "test2"
FAKE_DIR_TEST2_HASH = [
	{"Hash": "QmStL6TPbJfMHQhHjoVT93kCynVx3GwLf7xwgrtScqABhU",
	 "Name": "test2",                 "Size": "297"},
	{"Hash": "QmV3n14G8iQoNG8zpHCUZnmQpcQbhEfhQZ8NHvUEdoiXAN",
	 "Name": "test2/high",            "Size": "114"},
	{"Hash": "QmZazHsY4nbhRTHTEp5SUWd4At6aSXia1kxEuywHTicayE",
	 "Name": "test2/high/five",       "Size": "64"},
	{"Hash": "QmW8tRcpqy5siMNAU9Lx3GADAxQbVUrx8XJGFDjkd6vqLT",
	 "Name": "test2/high/five/dummy", "Size": "13"},
	{"Hash": "Qmb1NPqPzdHCMvHRfCkk6TWLcnpGJ71KnafacCMm6TKLcD",
	 "Name": "test2/fssdf",           "Size": "22"},
	{"Hash": "QmNuvmuFeeWWpxjCQwLkHshr8iqhGLWXFzSGzafBeawTTZ",
	 "Name": "test2/llllg",           "Size": "17"}
]

### test_add_filepattern_from_dirname
FAKE_DIR_FNPATTERN1 = "**/fss*"
# The hash of the folder is not same as above because the content of the folder added is not same
FAKE_DIR_FNPATTERN1_HASH = [
	{"Hash": "Qmb1NPqPzdHCMvHRfCkk6TWLcnpGJ71KnafacCMm6TKLcD",
	 "Name": "fake_dir/test2/fssdf", "Size": "22"},
	{"Hash": "QmT5rV6EsKNSW619SntLrkCxbUXXQh4BrKm3JazF2zEgEe",
	 "Name": "fake_dir/test2",       "Size": "73"},
	{"Hash": "QmbPzQruAEFjUU3gQfupns6b8USr8VrD9H71GrqGDXQSxm",
	 "Name": "fake_dir",             "Size": "124"}
]

## test_add_filepattern_subdir_wildcard
FAKE_DIR_FNPATTERN2 = "test2/**/high"
FAKE_DIR_FNPATTERN2_HASH = [
	{"Hash": "QmUXuNHpV6cdeTngSkEMbP2nQDPuyE2MFXNYtTXzZvLZHf",
	 "Name": "fake_dir",                       "Size": "216"},
	{"Hash": "QmZGuwqaXMmSwJcfTsvseHwy3mvDPD9zrs9WVowAZcQN4W",
	 "Name": "fake_dir/test2",                 "Size": "164"},
	{"Hash": "QmV3n14G8iQoNG8zpHCUZnmQpcQbhEfhQZ8NHvUEdoiXAN",
	 "Name": "fake_dir/test2/high",            "Size": "114"},
	{"Hash": "QmZazHsY4nbhRTHTEp5SUWd4At6aSXia1kxEuywHTicayE",
	 "Name": "fake_dir/test2/high/five",       "Size": "64"},
	{"Hash": "QmW8tRcpqy5siMNAU9Lx3GADAxQbVUrx8XJGFDjkd6vqLT",
	 "Name": "fake_dir/test2/high/five/dummy", "Size": "13"}
]


## test_add_recursive
FAKE_DIR_PATH = conftest.TEST_DIR / "fake_dir"
FAKE_DIR_HASH = [
	{"Hash": "QmNx8xVu9mpdz9k6etbh2S8JwZygatsZVCH4XhgtfUYAJi",
	 "Name": "fake_dir",                       "Size": "610"},
	{"Hash": "QmQcCtMgLVwvMQGu6mvsRYLjwqrZJcYtH4mboM9urWW9vX",
	 "Name": "fake_dir/fsdfgh",                "Size": "16"},
	{"Hash": "QmYAhvKYu46rh5NcHzeu6Bhc7NG9SqkF9wySj2jvB74Rkv",
	 "Name": "fake_dir/popoiopiu",             "Size": "23"},
	{"Hash": "QmStL6TPbJfMHQhHjoVT93kCynVx3GwLf7xwgrtScqABhU",
	 "Name": "fake_dir/test2",                 "Size": "297"},
	{"Hash": "Qmb1NPqPzdHCMvHRfCkk6TWLcnpGJ71KnafacCMm6TKLcD",
	 "Name": "fake_dir/test2/fssdf",           "Size": "22"},
	{"Hash": "QmV3n14G8iQoNG8zpHCUZnmQpcQbhEfhQZ8NHvUEdoiXAN",
	 "Name": "fake_dir/test2/high",            "Size": "114"},
	{"Hash": "QmZazHsY4nbhRTHTEp5SUWd4At6aSXia1kxEuywHTicayE",
	 "Name": "fake_dir/test2/high/five",       "Size": "64"},
	{"Hash": "QmW8tRcpqy5siMNAU9Lx3GADAxQbVUrx8XJGFDjkd6vqLT",
	 "Name": "fake_dir/test2/high/five/dummy", "Size": "13"},
	{"Hash": "QmNuvmuFeeWWpxjCQwLkHshr8iqhGLWXFzSGzafBeawTTZ",
	 "Name": "fake_dir/test2/llllg",           "Size": "17"},
	{"Hash": "QmRphRr6ULDEj7YnXpLdnxhnPiVjv5RDtGX3er94Ec6v4Q",
	 "Name": "fake_dir/test3",                 "Size": "76"},
	{"Hash": "QmeMbJSHNCesAh7EeopackUdjutTJznum1Fn7knPm873Fe",
	 "Name": "fake_dir/test3/ppppoooooooooo",  "Size": "16"}
]


def calc_path_rel_to_cwd(p):
	p = str(p)  # for Python < 3.5
	prefix = os.path.commonprefix([p, os.getcwd()])
	relpath = os.path.relpath(p, prefix)
	assert not os.path.isabs(relpath)
	return relpath


def test_add_single_from_str_with_dir(client, cleanup_pins):
	res = client.add(FAKE_FILE1_PATH, wrap_with_directory=True)
	
	assert FAKE_FILE1_DIR_HASH == res
	
	dir_hash = None
	for item in res:
		if item["Name"] == "":
			dir_hash = item["Hash"]
	assert dir_hash in client.pin.ls(type="recursive")["Keys"]


def test_only_hash_file(client):
	client.repo.gc()
	
	res = client.add(FAKE_FILE1_PATH, only_hash=True)
	
	assert FAKE_FILE1_HASH == res
	
	assert res["Hash"] not in client.pin.ls(type="recursive")
	assert res["Hash"] not in list(map(lambda i: i["Ref"], client.unstable.refs.local()))


def test_add_multiple_from_list(client, cleanup_pins):
	res = client.add(FAKE_FILE1_PATH, FAKE_FILE2_PATH)
	assert FAKE_FILES_HASH == res


def test_add_with_raw_leaves(client, cleanup_pins):
	res = client.add(FAKE_FILE1_PATH, raw_leaves=True)
	check_add_with_raw_leaves(client, res)


def check_add_with_raw_leaves(client, res):
	assert FAKE_FILE1_RAW_LEAVES_HASH == res
	assert res["Hash"] in client.pin.ls(type="recursive")["Keys"]


def test_add_nocopy_without_raw_leaves(client):
	error_msg = None
	try:
		client.add(FAKE_FILE1_PATH, nocopy=True, raw_leaves=False)
	except ipfshttpclient.exceptions.ErrorResponse as exc:
		error_msg = exc.args[0]
	assert error_msg is not None and "--raw-leaves" in error_msg


def test_nocopy_with_raw_leaves_file(client, cleanup_pins):
	res = client.add(FAKE_FILE1_PATH, nocopy=True, raw_leaves=True)
	check_no_copy(client, res)


def test_nocopy_with_default_raw_leaves_file(client, cleanup_pins):
	res = client.add(FAKE_FILE1_PATH, nocopy=True)
	check_no_copy(client, res)


def check_no_copy(client, res):
	check_add_with_raw_leaves(client, res)
	# TODO: assert client.filestore.ls(res["Hash"])["Status"] == 0
	# TODO: assert client.filestore.verify(res["Hash"])["Status"] == 0


def test_add_relative_path(client, cleanup_pins):
	res = client.add(calc_path_rel_to_cwd(FAKE_FILE1_PATH))
	assert FAKE_FILE1_HASH == res
	assert res["Hash"] in client.pin.ls(type="recursive")["Keys"]


def test_add_nocopy_with_relative_path(client):
	error_msg = None
	try:
		client.add(calc_path_rel_to_cwd(FAKE_FILE1_PATH), nocopy=True)
	except ipfshttpclient.exceptions.ErrorResponse as exc:
		error_msg = exc.args[0]

	# For relative paths, multipart streaming layer won't append the
	# Abspath header, and server will report the missing header. Note that
	# currently, the server does report an error if Abspath is present but
	# is a relative or nonexistent path -- instead, it silently ignores
	# nocopy and adds the file to the blockstore (bug).
	assert error_msg is not None and "missing file path" in error_msg


def test_add_multiple_from_dirname(client, cleanup_pins):
	res = client.add(FAKE_DIR_TEST2_PATH)
	assert conftest.sort_by_key(FAKE_DIR_TEST2_HASH) == conftest.sort_by_key(res)


def test_add_filepattern_from_dirname(client, cleanup_pins):
	res = client.add(FAKE_DIR_PATH, pattern=FAKE_DIR_FNPATTERN1)
	assert conftest.sort_by_key(FAKE_DIR_FNPATTERN1_HASH) == conftest.sort_by_key(res)


def test_add_filepattern_subdir_wildcard(client, cleanup_pins):
	res = client.add(FAKE_DIR_PATH, pattern=FAKE_DIR_FNPATTERN2)
	assert conftest.sort_by_key(FAKE_DIR_FNPATTERN2_HASH) == conftest.sort_by_key(res)


def test_add_recursive(client, cleanup_pins):
	res = client.add(FAKE_DIR_PATH, recursive=True)
	assert conftest.sort_by_key(FAKE_DIR_HASH) == conftest.sort_by_key(res)


def test_get_file(client, cleanup_pins):
	client.add(FAKE_FILE1_PATH)
	
	test_hash = FAKE_DIR_HASH[1]["Hash"]
	
	try:
		client.get(test_hash)
		assert test_hash in os.listdir(os.getcwd())
	finally:
		os.remove(test_hash)
		assert test_hash not in os.listdir(os.getcwd())


def test_get_dir(client, cleanup_pins):
	client.add(FAKE_DIR_PATH, recursive=True)

	test_hash = FAKE_DIR_HASH[0]["Hash"]
	
	try:
		client.get(test_hash)
		assert test_hash in os.listdir(os.getcwd())
	finally:
		shutil.rmtree(test_hash)
		assert test_hash not in os.listdir(os.getcwd())


def test_get_path(client, cleanup_pins):
	client.add(FAKE_FILE1_PATH)
	
	test_hash = FAKE_DIR_HASH[0]["Hash"] + "/fsdfgh"
	
	try:
		client.get(test_hash)
		assert "fsdfgh" in os.listdir(os.getcwd())
	finally:
		os.remove("fsdfgh")
		assert "fsdfgh" not in os.listdir(os.getcwd())


def test_cat_single_file_str(client, cleanup_pins):
	client.add(FAKE_FILE1_PATH)
	
	content = client.cat("QmQcCtMgLVwvMQGu6mvsRYLjwqrZJcYtH4mboM9urWW9vX")
	assert content == b"dsadsad\n"


def test_cat_file_block(client, cleanup_pins):
	client.add(FAKE_FILE1_PATH)

	content = b"dsadsad\n"
	for offset in range(len(content)):
		for length in range(len(content)):
			block = client.cat("QmQcCtMgLVwvMQGu6mvsRYLjwqrZJcYtH4mboM9urWW9vX",
			                   offset=offset, length=length)
			assert block == content[offset:(offset + length)]


##################################################
# Mutable File System (MFS) aka `client.files.*` #
##################################################
TEST_MFS_FILES = {
	"test_file1": {
		"Name": conftest.TEST_DIR / "fake_dir" / "popoiopiu",
		"Stat": {
			u"Type": "file",
			u"Hash": "QmUvobKqcCE56brA8pGTRRRsGy2SsDEKSxFLZkBQFv7Vvv",
			u"Blocks": 1,
			u"CumulativeSize": 73,
			u"Size": 15
		}
	}
}

TEST_MFS_DIRECTORY = "/test_dir"


def test_mfs_file_cp_rm(client, cleanup_pins):
	res = client.add(FAKE_FILE1_PATH)
	h = res["Hash"]

	mfs_path = "/" + TEST_MFS_DIRECTORY + "file1"
	res = client.files.cp("/ipfs/" + h, mfs_path)
	assert res is None

	res = client.files.rm(mfs_path)
	assert res is None


def test_mfs_file_write_stat_read_delete(client):
	for filename, desc in TEST_MFS_FILES.items():
		filepath = "/" + filename

		# Create target file
		client.files.write(filepath, desc["Name"], create=True)

		# Verify stat information of file
		stat = client.files.stat(filepath)
		assert sorted(desc["Stat"].items()) == sorted(stat.items())

		# Read back (and compare file contents)
		with open(str(desc["Name"]), "rb") as file:
			content = client.files.read(filepath)
			assert content == file.read()

		# Remove file
		client.files.rm(filepath)


def test_mfs_dir_make_fill_list_delete(client):
	client.files.mkdir(TEST_MFS_DIRECTORY)
	for filename, desc in TEST_MFS_FILES.items():
		# Create target file in directory
		client.files.write(
			TEST_MFS_DIRECTORY + "/" + filename,
			desc["Name"], create=True
		)

	# Verify directory contents
	contents = client.files.ls(TEST_MFS_DIRECTORY)[u"Entries"]
	filenames1 = list(map(lambda d: d["Name"], contents))
	filenames2 = list(TEST_MFS_FILES.keys())
	assert filenames1 == filenames2

	# Remove directory
	client.files.rm(TEST_MFS_DIRECTORY, recursive=True)

	with pytest.raises(ipfshttpclient.exceptions.Error):
		client.files.stat(TEST_MFS_DIRECTORY)