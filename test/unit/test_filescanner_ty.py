
from ipfshttpclient.filescanner_ty import FSNodeEntry, FSNodeType


def test_fs_node_entry_as_repr() -> None:
	entry = FSNodeEntry(type=FSNodeType.FILE, path='b', relpath='c', name='d', parentfd=123)

	assert (
		repr(entry)
		==
		"FSNodeEntry(type=<FSNodeType.FILE: 1>, path='b', relpath='c', name='d', parentfd=123)"
	)


def test_fs_node_entry_as_str() -> None:
	entry = FSNodeEntry(type=FSNodeType.FILE, path='b', relpath='c', name='d', parentfd=123)

	assert str(entry) == 'b'
