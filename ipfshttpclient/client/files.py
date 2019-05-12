# -*- coding: utf-8 -*-
from __future__ import absolute_import

from . import base

from .. import multipart


class Section(base.SectionBase):
	"""
	Functions used to manage files in IPFS's virtual “Mutable File System” (MFS)
	file storage space.
	"""
	
	@base.returns_no_item
	def cp(self, source, dest, **kwargs):
		"""Copies files within the MFS.

		Due to the nature of IPFS this will not actually involve any of the
		file's content being copied.

		.. code-block:: python

			>>> client.files.ls("/")
			{'Entries': [
				{'Size': 0, 'Hash': '', 'Name': 'Software', 'Type': 0},
				{'Size': 0, 'Hash': '', 'Name': 'test', 'Type': 0}
			]}
			>>> client.files.cp("/test", "/bla")
			>>> client.files.ls("/")
			{'Entries': [
				{'Size': 0, 'Hash': '', 'Name': 'Software', 'Type': 0},
				{'Size': 0, 'Hash': '', 'Name': 'bla', 'Type': 0},
				{'Size': 0, 'Hash': '', 'Name': 'test', 'Type': 0}
			]}

		Parameters
		----------
		source : str
			Filepath within the MFS to copy from
		dest : str
			Destination filepath within the MFS to which the file will be
			copied to
		"""
		args = (source, dest)
		return self._client.request('/files/cp', args, **kwargs)


	#TODO: Add `flush(path="/")`


	@base.returns_single_item
	def ls(self, path, **kwargs):
		"""Lists contents of a directory in the MFS.

		.. code-block:: python

			>>> client.files.ls("/")
			{'Entries': [
				{'Size': 0, 'Hash': '', 'Name': 'Software', 'Type': 0}
			]}

		Parameters
		----------
		path : str
			Filepath within the MFS

		Returns
		-------
			dict
		
		+---------+------------------------------------------+
		| Entries | List of files in the given MFS directory |
		+---------+------------------------------------------+
		"""
		args = (path,)
		return self._client.request('/files/ls', args, decoder='json', **kwargs)
	
	
	@base.returns_no_item
	def mkdir(self, path, parents=False, **kwargs):
		"""Creates a directory within the MFS.

		.. code-block:: python

			>>> client.files.mkdir("/test")

		Parameters
		----------
		path : str
			Filepath within the MFS
		parents : bool
			Create parent directories as needed and do not raise an exception
			if the requested directory already exists
		"""
		kwargs.setdefault("opts", {})["parents"] = parents

		args = (path,)
		return self._client.request('/files/mkdir', args, **kwargs)
	
	
	@base.returns_no_item
	def mv(self, source, dest, **kwargs):
		"""Moves files and directories within the MFS.

		.. code-block:: python

			>>> client.files.mv("/test/file", "/bla/file")

		Parameters
		----------
		source : str
			Existing filepath within the MFS
		dest : str
			Destination to which the file will be moved in the MFS
		"""
		args = (source, dest)
		return self._client.request('/files/mv', args, **kwargs)
	
	
	def read(self, path, offset=0, count=None, **kwargs):
		"""Reads a file stored in the MFS.

		.. code-block:: python

			>>> client.files.read("/bla/file")
			b'hi'

		Parameters
		----------
		path : str
			Filepath within the MFS
		offset : int
			Byte offset at which to begin reading at
		count : int
			Maximum number of bytes to read

		Returns
		-------
			bytes : MFS file contents
		"""
		opts = {"offset": offset}
		if count is not None:
			opts["count"] = count
		kwargs.setdefault("opts", {}).update(opts)

		args = (path,)
		return self._client.request('/files/read', args, **kwargs)
	
	
	@base.returns_no_item
	def rm(self, path, recursive=False, **kwargs):
		"""Removes a file from the MFS.

		.. code-block:: python

			>>> client.files.rm("/bla/file")

		Parameters
		----------
		path : str
			Filepath within the MFS
		recursive : bool
			Recursively remove directories?
		"""
		kwargs.setdefault("opts", {})["recursive"] = recursive

		args = (path,)
		return self._client.request('/files/rm', args, **kwargs)
	
	
	@base.returns_single_item
	def stat(self, path, **kwargs):
		"""Returns basic ``stat`` information for an MFS file
		(including its hash).

		.. code-block:: python

			>>> client.files.stat("/test")
			{'Hash': 'QmUNLLsPACCz1vLxQVkXqqLX5R1X345qqfHbsf67hvA3Nn',
			 'Size': 0, 'CumulativeSize': 4, 'Type': 'directory', 'Blocks': 0}

		Parameters
		----------
		path : str
			Filepath within the MFS

		Returns
		-------
			dict : MFS file information
		"""
		args = (path,)
		return self._client.request('/files/stat', args, decoder='json', **kwargs)
	
	
	@base.returns_no_item
	def write(self, path, file, offset=0, create=False, truncate=False, count=None, **kwargs):
		"""Writes to a mutable file in the MFS.

		.. code-block:: python

			>>> client.files.write("/test/file", io.BytesIO(b"hi"), create=True)

		Parameters
		----------
		path : str
			Filepath within the MFS
		file : Union[str, bytes, os.PathLike, io.RawIOBase, int]
			IO stream object with data that should be written
		offset : int
			Byte offset at which to begin writing at
		create : bool
			Create the file if it does not exist
		truncate : bool
			Truncate the file to size zero before writing
		count : int
			Maximum number of bytes to read from the source ``file``
		"""
		opts = {"offset": offset, "create": create, "truncate": truncate}
		if count is not None:
			opts["count"] = count
		kwargs.setdefault("opts", {}).update(opts)

		args = (path,)
		body, headers = multipart.stream_files(file, self.chunk_size)
		return self._client.request('/files/write', args, data=body, headers=headers, **kwargs)


class Base(base.ClientBase):
	files = base.SectionProperty(Section)
	
	
	def add(self, file, *files, **kwargs):
		"""Add a file, or directory of files to IPFS.

		.. code-block:: python

			>>> with io.open('nurseryrhyme.txt', 'w', encoding='utf-8') as f:
			...	 numbytes = f.write('Mary had a little lamb')
			>>> client.add('nurseryrhyme.txt')
			{'Hash': 'QmZfF6C9j4VtoCsTp4KSrhYH47QMd3DNXVZBKaxJdhaPab',
			 'Name': 'nurseryrhyme.txt'}

		Parameters
		----------
		file : Union[str, bytes, os.PathLike, int, io.IOBase]
			A filepath, path-object, file descriptor or open file object the
			file or directory to add
		recursive : bool
			If ``file`` is some kind of directory, controls whether files in
			subdirectories should also be added or not (Default: ``False``)
		pattern : Union[str, list]
			Single `*glob* <https://docs.python.org/3/library/glob.html>`_
			pattern or list of *glob* patterns and compiled regular expressions
			to match the names of the filepaths to keep
		trickle : bool
			Use trickle-dag format (optimized for streaming) when generating
			the dag; see `the FAQ <https://github.com/ipfs/faq/issues/218>` for
			more information (Default: ``False``)
		only_hash : bool
			Only chunk and hash, but do not write to disk (Default: ``False``)
		wrap_with_directory : bool
			Wrap files with a directory object to preserve their filename
			(Default: ``False``)
		chunker : str
			The chunking algorithm to use
		pin : bool
			Pin this object when adding (Default: ``True``)
		raw_leaves : bool
			Use raw blocks for leaf nodes. (experimental). (Default: ``True``
			when ``nocopy`` is True, or ``False`` otherwise)
		nocopy : bool
			Add the file using filestore. Implies raw-leaves. (experimental).
			(Default: ``False``)

		Returns
		-------
			Union[dict, list]
				File name and hash of the added file node, will return a list
				of one or more items unless only a single file was given
		"""
		#PY2: No support for kw-only parameters after glob parameters
		recursive = kwargs.pop("recursive", False)
		pattern   = kwargs.pop("pattern", "**")
		nocopy = kwargs.pop("nocopy", False)
		opts = {
			"trickle": kwargs.pop("trickle", False),
			"only-hash": kwargs.pop("only_hash", False),
			"wrap-with-directory": kwargs.pop("wrap_with_directory", False),
			"pin": kwargs.pop("pin", True),
			"raw-leaves": kwargs.pop("raw_leaves", nocopy),
			'nocopy':  nocopy
		}
		if "chunker" in kwargs:
			opts["chunker"] = kwargs.pop("chunker")
		kwargs.setdefault("opts", {}).update(opts)

		assert not isinstance(file, (tuple, list)), \
		       "Use `client.add(name1, name2, …)` to add several items"
		multiple = (len(files) > 0)
		to_send  = ((file,) + files) if multiple else file
		body, headers, is_dir = multipart.stream_filesystem_node(
			to_send, recursive, pattern, self.chunk_size
		)
		
		resp = self._client.request('/add', decoder='json', data=body, headers=headers, **kwargs)
		if not multiple and not is_dir and not kwargs["opts"]["wrap-with-directory"]:
			assert len(resp) == 1
			return resp[0]
		return resp
	
	
	def get(self, cid, **kwargs):
		"""Downloads a file, or directory of files from IPFS.

		Files are placed in the current working directory.

		Parameters
		----------
		cid : Union[str, cid.CIDv0, cid.CIDv1]
			The path to the IPFS object(s) to be outputted
		"""
		args = (str(cid),)
		return self._client.download('/get', args, **kwargs)
	
	
	def cat(self, cid, offset=0, length=-1, **kwargs):
		r"""Retrieves the contents of a file identified by hash.

		.. code-block:: python

			>>> client.cat('QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDxdXBFca7D')
			Traceback (most recent call last):
			  ...
			ipfsapi.exceptions.Error: this dag node is a directory
			>>> client.cat('QmeKozNssnkJ4NcyRidYgDY2jfRZqVEoRGfipkgath71bX')
			b'<!DOCTYPE html>\n<html>\n\n<head>\n<title>ipfs example viewer</…'

		Parameters
		----------
		cid : Union[str, cid.CIDv0, cid.CIDv1]
			The name or path of the IPFS object(s) to be retrieved
		offset : int
			Byte offset to begin reading from
		length : int
			Maximum number of bytes to read(-1 for all)

		Returns
		-------
			bytes
				The file's contents
		"""
		args = (str(cid),)
		opts = {}
		if offset != 0:
			opts['offset'] = offset
		if length != -1:
			opts['length'] = length
		kwargs.setdefault('opts', opts)
		return self._client.request('/cat', args, **kwargs)
	
	
	@base.returns_single_item
	def ls(self, cid, **kwargs):
		"""Returns a list of objects linked to by the given hash.

		.. code-block:: python

			>>> client.ls('QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDxdXBFca7D')
			{'Objects': [
				{'Hash': 'QmTkzDwWqPbnAh5YiV5VwcTLnGdwSNsNTn2aDxdXBFca7D',
					'Links': [
						{'Hash': 'Qmd2xkBfEwEs9oMTk77A6jrsgurpF3ugXSg7dtPNFkcNMV',
						 'Name': 'Makefile',          'Size': 174, 'Type': 2},
						…
						{'Hash': 'QmSY8RfVntt3VdxWppv9w5hWgNrE31uctgTiYwKir8eXJY',
						 'Name': 'published-version', 'Size': 55,  'Type': 2}
					]
				}
			]}

		Parameters
		----------
		cid : Union[str, cid.CIDv0, cid.CIDv1]
			The path to the IPFS object(s) to list links from

		Returns
		-------
			dict
				Directory information and contents
		"""
		args = (str(cid),)
		return self._client.request('/ls', args, decoder='json', **kwargs)
