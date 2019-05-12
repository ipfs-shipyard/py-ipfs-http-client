"""HTTP :mimetype:`multipart/*`-encoded file streaming.
"""
from __future__ import absolute_import

import abc
import inspect
import os
import re
from six.moves import urllib
import uuid

import six

from . import utils


default_chunk_size = 4096


#PY34: String formattings for binary types not supported
if hasattr(six.binary_type, "__mod__"):
	def bytes_fmt(b, *a):
		return b % a
else:
	def bytes_fmt(base, *args):
		# Decode each argument as ISO-8859-1 which causes each by to be
		# reinterpreted as character
		base = base.decode("iso-8859-1")
		args = tuple(map(lambda b: bytes(b).decode("iso-8859-1"), args))

		# Apply format and convert back
		return (base % args).encode("iso-8859-1")


def content_disposition_headers(filename, disptype="form-data"):
	"""Returns a dict containing the MIME content-disposition header for a file.

	.. code-block:: python

		>>> content_disposition_headers('example.txt')
		{'Content-Disposition': 'form-data; filename="example.txt"'}

		>>> content_disposition_headers('example.txt', 'attachment')
		{'Content-Disposition': 'attachment; filename="example.txt"'}

	Parameters
	----------
	filename : str
		Filename to retrieve the MIME content-disposition for
	disptype : str
		Rhe disposition type to use for the file
	"""
	disp = '%s; filename="%s"' % (
		disptype,
		urllib.parse.quote(filename, safe='')
	)
	return {'Content-Disposition': disp}


def content_type_headers(filename, content_type=None):
	"""Returns a dict with the content-type header for a file.

	Guesses the mimetype for a filename and returns a dict
	containing the content-type header.

	.. code-block:: python

		>>> content_type_headers('example.txt')
		{'Content-Type': 'text/plain'}

		>>> content_type_headers('example.jpeg')
		{'Content-Type': 'image/jpeg'}

		>>> content_type_headers('example')
		{'Content-Type': 'application/octet-stream'}

	Parameters
	----------
	filename : str
		Filename to guess the content-type for
	content_type : str
		The Content-Type to use; if not set a content type will be guessed
	"""
	return {'Content-Type': content_type if content_type else utils.guess_mimetype(filename)}


def multipart_content_type_headers(boundary, subtype='mixed'):
	"""Creates a MIME multipart header with the given configuration.

	Returns a dict containing a MIME multipart header with the given
	boundary.

	.. code-block:: python

		>>> multipart_content_type_headers('8K5rNKlLQVyreRNncxOTeg')
		{'Content-Type': 'multipart/mixed; boundary="8K5rNKlLQVyreRNncxOTeg"'}

		>>> multipart_content_type_headers('8K5rNKlLQVyreRNncxOTeg', 'alt')
		{'Content-Type': 'multipart/alt; boundary="8K5rNKlLQVyreRNncxOTeg"'}

	Parameters
	----------
	boundary : str
		The content delimiter to put into the header
	subtype : str
		The subtype in :mimetype:`multipart/*`-domain to put into the header
	"""
	ctype = 'multipart/%s; boundary="%s"' % (
		subtype,
		boundary
	)
	return {'Content-Type': ctype}



class StreamBase(object):
	"""Generator that encodes multipart/form-data.

	An abstract buffered generator class which encodes
	:mimetype:`multipart/form-data`.

	Parameters
	----------
	name : str
		The name of the file to encode
	chunk_size : int
		The maximum size that any single file chunk may have in bytes
	"""

	__metaclass__ = abc.ABCMeta

	def __init__(self, name, chunk_size=default_chunk_size):
		self.chunk_size = chunk_size
		self.name = name

		self._boundary = uuid.uuid4().hex

		self._headers = content_disposition_headers(name, disptype='form-data')
		self._headers.update(multipart_content_type_headers(self._boundary, subtype='form-data'))

		#WORKAROUND: Go-IPFS randomly fucks up streaming requests if they are not
		#            `Connection: close` (https://github.com/ipfs/go-ipfs/issues/5168)
		self._headers["Connection"] = "close"

		super(StreamBase, self).__init__()

	def headers(self):
		return self._headers.copy()

	@abc.abstractmethod
	def _body(self, *args, **kwargs):
		"""Yields the body of this stream with chunks of undefined size.
		"""

	def body(self, *args, **kwargs):
		"""Yields the body of this stream.
		"""
		# Cap all returned body chunks to the given chunk size
		#PY2: Use `yield from` instead
		for chunk in self._gen_chunks(self._body()): yield chunk

	def _gen_headers(self, headers):
		"""Yields the HTTP header text for some content.

		Parameters
		----------
		headers : dict
			The headers to yield
		"""
		for name, value in sorted(headers.items(), key=lambda i: i[0]):
			yield bytes_fmt(b"%s: %s\r\n", name.encode("ascii"), value.encode("utf-8"))
		yield b"\r\n"

	def _gen_chunks(self, gen):
		"""Generates byte chunks of a given size.

		Takes a bytes generator and yields chunks of a maximum of
		``chunk_size`` bytes.

		Parameters
		----------
		gen : generator
			The bytes generator that produces the bytes
		"""
		for data in gen:
			#PERF: This is zero-copy if `len(data) <= self.chunk_size`
			for offset in range(0, len(data), self.chunk_size):
				yield data[offset:self.chunk_size]

	def _gen_item_start(self):
		"""Yields the body section for the content.
		"""
		yield bytes_fmt(b"--%s\r\n", self._boundary.encode("ascii"))

	def _gen_item_end(self):
		"""Yields the body section for the content.
		"""
		yield b"\r\n"

	def _gen_end(self):
		"""Yields the closing text of a multipart envelope."""
		yield bytes_fmt(b'--%s--\r\n', self._boundary.encode("ascii"))


class StreamFileMixin(object):
	def _gen_file(self, filename, file_location=None, file=None, content_type=None):
		"""Yields the entire contents of a file.

		Parameters
		----------
		filename : str
			Filename of the file being opened and added to the HTTP body
		file_location : str
			Full path to the file being added, including the filename
		file : io.RawIOBase
			The binary file-like object whose contents should be streamed

			No contents will be streamed if this is ``None``.
		content_type : str
			The Content-Type of the file; if not set a value will be guessed
		"""
		#PY2: Use `yield from` instead
		for chunk in self._gen_file_start(filename, file_location, content_type):
			yield chunk
		if file:
			for chunk in self._gen_file_chunks(file): yield chunk
		for chunk in self._gen_file_end(): yield chunk

	def _gen_file_start(self, filename, file_location=None, content_type=None):
		"""Yields the opening text of a file section in multipart HTTP.

		Parameters
		----------
		filename : str
			Filename of the file being opened and added to the HTTP body
		file_location : str
			Full path to the file being added, including the filename
		content_type : str
			The Content-Type of the file; if not set a value will be guessed
		"""
		#PY2: Use `yield from` instead
		for chunk in self._gen_item_start(): yield chunk

		headers = content_disposition_headers(filename.replace(os.sep, "/"), disptype="file")
		headers.update(content_type_headers(filename, content_type))
		if file_location and os.path.isabs(file_location):
			headers.update({"Abspath": file_location})
		#PY2: Use `yield from` instead
		for chunk in self._gen_headers(headers): yield chunk

	def _gen_file_chunks(self, file):
		"""Yields chunks of a file.

		Parameters
		----------
		fp : io.RawIOBase
			The file to break into chunks
			(must be an open file or have the ``readinto`` method)
		"""
		while True:
			buf = file.read(self.chunk_size)
			if len(buf) < 1:
				break
			yield buf

	def _gen_file_end(self):
		"""Yields the end text of a file section in HTTP multipart encoding."""
		return self._gen_item_end()


class FilesStream(StreamBase, StreamFileMixin):
	"""Generator that encodes multiples files into HTTP multipart.

	A buffered generator that encodes an array of files as
	:mimetype:`multipart/form-data`. This is a concrete implementation of
	:class:`~ipfsapi.multipart.StreamBase`.

	Parameters
	----------
	files : Union[str, bytes, os.PathLike, io.IOBase, int, collections.abc.Iterable]
		The name, file object or file descriptor of the file to encode; may also
		be a list of several items to allow for more efficient batch processing
	chunk_size : int
		The maximum size that any single file chunk may have in bytes
	"""
	def __init__(self, files, name="files", chunk_size=default_chunk_size):
		self.files = utils.clean_files(files)

		super(FilesStream, self).__init__(name, chunk_size=chunk_size)

	def _body(self):
		"""Yields the body of the buffered file."""
		for file, need_close in self.files:
			try:
				try:
					file_location = file.name
					filename = os.path.basename(file_location)
				except AttributeError:
					file_location = None
					filename = ''

				#PY2: Use `yield from` instead
				for chunk in self._gen_file(filename, file_location, file):
					yield chunk
			finally:
				if need_close:
					file.close()

		#PY2: Use `yield from` instead
		for chunk in self._gen_end(): yield chunk


def glob_compile(pat):
	"""Translate a shell glob PATTERN to a regular expression.

	Source code taken from the `fnmatch.translate` function of the python 3.7
	standard-library with the glob-style modification of making `*`
	non-recursive and the adding `**` as recursive matching operator.
	"""

	i, n = 0, len(pat)
	res = ''
	while i < n:
		c = pat[i]
		i = i + 1
		if c == '/' and len(pat) > (i + 2) and pat[i:(i + 3)] == '**/':
			# Special-case for "any number of sub-directories" operator since
			# may also expand to no entries:
			#  Otherwise `a/**/b` would expand to `a[/].*[/]b` which wouldn't
			#  match the immediate sub-directories of `a`, like `a/b`.
			i = i + 3
			res = res + '[/]([^/]*[/])*'
		elif c == '*':
			if len(pat) > i and pat[i] == '*':
				i = i + 1
				res = res + '.*'
			else:
				res = res + '[^/]*'
		elif c == '?':
			res = res + '[^/]'
		elif c == '[':
			j = i
			if j < n and pat[j] == '!':
				j = j + 1
			if j < n and pat[j] == ']':
				j = j + 1
			while j < n and pat[j] != ']':
				j = j + 1
			if j >= n:
				res = res + '\\['
			else:
				stuff = pat[i:j]
				if '--' not in stuff:
					stuff = stuff.replace('\\', r'\\')
				else:
					chunks = []
					k = i + 2 if pat[i] == '!' else i + 1
					while True:
						k = pat.find('-', k, j)
						if k < 0:
							break
						chunks.append(pat[i:k])
						i = k + 1
						k = k + 3
					chunks.append(pat[i:j])
					# Escape backslashes and hyphens for set difference (--).
					# Hyphens that create ranges shouldn't be escaped.
					stuff = '-'.join(s.replace('\\', r'\\').replace('-', r'\-')
					                 for s in chunks)
				# Escape set operations (&&, ~~ and ||).
				stuff = re.sub(r'([&~|])', r'\\\1', stuff)
				i = j + 1
				if stuff[0] == '!':
					stuff = '^' + stuff[1:]
				elif stuff[0] in ('^', '['):
					stuff = '\\' + stuff
				res = '%s[%s]' % (res, stuff)
		else:
			res = res + re.escape(c)
	return re.compile(r'^' + res + r'\Z$', flags=re.M | re.S)


class DirectoryStream(StreamBase, StreamFileMixin):
	"""Generator that encodes a directory into HTTP multipart.

	A buffered generator that encodes an array of files as
	:mimetype:`multipart/form-data`. This is a concrete implementation of
	:class:`~ipfshttpclient.multipart.StreamBase`.

	Parameters
	----------
	directory : Union[str, os.PathLike, int]
		The filepath or file descriptor of the directory to encode

		File descriptors are only supported on Unix and Python 3.
	dirname : Union[str, None]
		The name of the base directroy to upload, use ``None`` for
		the default of ``os.path.basename(directory) or '.'``
	patterns : Union[str, re.compile, collections.abc.Iterable]
		A single glob pattern or a list of several glob patterns and
		compiled regular expressions used to determine which filepaths to match
	chunk_size : int
		The maximum size that any single file chunk may have in bytes
	"""
	def __init__(self, directory,
	             recursive=False, patterns='**', dirname=None,
	             chunk_size=default_chunk_size):
		self.patterns = []
		patterns = [patterns] if isinstance(patterns, str) else patterns
		for pattern in patterns:
			self.patterns.append(glob_compile(pattern) if isinstance(pattern, str) else pattern)

		self.directory = utils.convert_path(directory)
		if not isinstance(self.directory, int):
			self.directory = os.path.normpath(self.directory)
		self.recursive = recursive
		self.dirname   = dirname

		name = os.path.basename(self.directory) if not isinstance(self.directory, int) else ""
		super(DirectoryStream, self).__init__(name, chunk_size=chunk_size)

	def _body_directory(self, short_path, visited_directories):
		# Do not continue if this directory has already been added
		if short_path in visited_directories:
			return

		# Scan for first super-directory that has already been added
		dir_base  = short_path
		dir_parts = []
		while dir_base:
			dir_base, dir_name = os.path.split(dir_base)
			dir_parts.append(dir_name)
			if dir_base in visited_directories:
				break

		# Add missing intermediate directory nodes in the right order
		while dir_parts:
			dir_base = os.path.join(dir_base, dir_parts.pop())

			# Generate directory as special empty file
			#PY2: Use `yield from` instead
			for chunk in self._gen_file(dir_base, content_type="application/x-directory"):
				yield chunk

			# Remember that this directory has already been sent
			visited_directories.add(dir_base)

	def _body_file(self, short_path, file_location, dir_fd=-1):
		try:
			if dir_fd >= 0:
				f_path_or_desc = os.open(file_location, os.O_RDONLY | os.O_CLOEXEC, dir_fd=dir_fd)
			else:
				f_path_or_desc = file_location
			# Stream file to client
			with open(f_path_or_desc, "rb") as file:
				#PY2: Use `yield from`
				for chunk in self._gen_file(short_path, file_location, file):
					yield chunk
		except OSError as e:
			print(e)
			# File might have disappeared between `os.walk()` and `open()`
			pass

	def _body(self):
		"""Streams the contents of the selected directory as binary chunks."""
		def match_short_path(short_path):
			# Remove initial path component so that all files are based in
			# the target directory itself (not one level above)
			if os.path.sep in short_path:
				path = short_path.split(os.path.sep, 1)[1]
			else:
				return False

			# Convert all path seperators to POSIX style
			path = path.replace(os.path.sep, '/')

			# Do the matching and the simplified path
			for pattern in self.patterns:
				if pattern.match(path):
					return True
			return False

		visited_directories = set()

		# Normalize directory path without destroying symlinks
		sep = os.path.sep
		directory = self.directory
		if not isinstance(self.directory, int):
			directory = os.fspath(directory) if hasattr(os, "fspath") else directory
			if not isinstance(directory, str):
				sep = os.fsencode(sep)
			while sep * 2 in directory:
				directory.replace(sep * 2, sep)
			if directory.endswith(sep):
				directory = directory[:-len(sep)]

		# Determine base directory name to send to IPFS (required and also used
		# as part of the wrap_with_directory feature)
		if self.dirname:
			dirname = self.dirname
		elif not isinstance(directory, int):
			dirname = os.path.basename(directory)
			dirname = dirname if isinstance(dirname, str) else os.fsdecode(dirname)
		else:
			dirname = "_"
		assert type(directory) == type(dirname) or isinstance(directory, int)

		# Identify the unnecessary portion of the relative path
		truncate = (directory if not isinstance(directory, int) else ".") + sep
		# Traverse the filesystem downward from the target directory's uri
		# Errors: `os.walk()` will simply return an empty generator if the
		#         target directory does not exist.
		wildcard_directories = set()

		if not isinstance(self.directory, int):
			walk_iter = os.walk(self.directory)
		else:
			walk_iter = os.fwalk(dir_fd=self.directory)
		for result in walk_iter:
			cur_dir, filenames = result[0], result[2]
			dir_fd = -1 if not isinstance(self.directory, int) else result[3]

			# find the path relative to the directory being added
			if len(truncate) > 0:
				_, _, short_path = cur_dir.partition(truncate)
			else:
				short_path = cur_dir
				# remove leading / or \ if it is present
				if short_path.startswith(os.path.sep):
					short_path = short_path[len(os.path.sep):]
			short_path = os.path.join(dirname, short_path) if short_path else dirname

			wildcard_directory = False
			if os.path.split(short_path)[0] in wildcard_directories:
				# Parent directory has matched a pattern, all sub-nodes should
				# be added too
				wildcard_directories.add(short_path)
				wildcard_directory = True
			else:
				# Check if directory path matches one of the patterns
				if match_short_path(short_path):
					# Directory matched pattern and it should therefor
					# be added along with all of its contents
					wildcard_directories.add(short_path)
					wildcard_directory = True

			# Always add directories within wildcard directories - even if they
			# are empty
			if wildcard_directory:
				#PY2: Use `yield from` instead
				for chunk in self._body_directory(short_path, visited_directories): yield chunk

			# Iterate across the files in the current directory
			for filename in filenames:
				# Find the filename relative to the directory being added
				short_file_path = os.path.join(short_path, filename)
				if dir_fd < 0:
					file_location = os.path.join(cur_dir, filename)
				else:
					file_location = filename

				if wildcard_directory:
					# Always add files in wildcard directories
					#PY2: Use `yield from` instead
					for chunk in self._body_file(short_file_path, file_location, dir_fd=dir_fd):
						yield chunk
				else:
					# Add file (and all missing intermediary directories)
					# if it matches one of the patterns
					if match_short_path(short_file_path):
						#PY2: Use `yield from` instead
						for chunk in self._body_directory(short_path, visited_directories):
							yield chunk
						for chunk in self._body_file(short_file_path, file_location, dir_fd=dir_fd):
							yield chunk

		#PY2: Use `yield from` instead
		for chunk in self._gen_end(): yield chunk


class BytesFileStream(FilesStream):
	"""A buffered generator that encodes bytes as file in
	:mimetype:`multipart/form-data`.

	Parameters
	----------
	data : bytes
		The binary data to stream to the daemon
	chunk_size : int
		The maximum size of a single data chunk
	"""
	def __init__(self, data, name="bytes", chunk_size=default_chunk_size):
		super(BytesFileStream, self).__init__([], name=name, chunk_size=chunk_size)

		self.data = data if inspect.isgenerator(data) else (data,)

	def body(self):
		"""Yields the encoded body."""
		#PY2: Use `yield from` instead
		for chunk in self._gen_file_start(self.name): yield chunk
		for chunk in self._gen_chunks(self.data): yield chunk
		for chunk in self._gen_file_end(): yield chunk
		for chunk in self._gen_end(): yield chunk


def stream_files(files, chunk_size=default_chunk_size):
	"""Gets a buffered generator for streaming files.

	Returns a buffered generator which encodes a file or list of files as
	:mimetype:`multipart/form-data` with the corresponding headers.

	Parameters
	----------
	files : Union[str, bytes, os.PathLike, io.IOBase, int, collections.abc.Iterable]
		The file(s) to stream
	chunk_size : int
		Maximum size of each stream chunk
	"""
	stream = FilesStream(files, chunk_size=chunk_size)
	return stream.body(), stream.headers()


def stream_directory(directory, recursive=False, patterns='**', chunk_size=default_chunk_size):
	"""Gets a buffered generator for streaming directories.

	Returns a buffered generator which encodes a directory as
	:mimetype:`multipart/form-data` with the corresponding headers.

	Parameters
	----------
	directory : Union[str, bytes, os.PathLike, int]
		The filepath of the directory to stream
	recursive : bool
		Stream all content within the directory recursively?
	patterns : Union[str, re.compile, collections.abc.Iterable]
		Single *glob* pattern or list of *glob* patterns and compiled
		regular expressions to match the names of the filepaths to keep
	chunk_size : int
		Maximum size of each stream chunk
	"""
	def stream_directory_impl(directory, dirname=None):
		stream = DirectoryStream(directory,
		                         recursive=recursive, patterns=patterns,
		                         dirname=dirname, chunk_size=chunk_size)
		return stream.body(), stream.headers()

	# Note that `os.fwalk` is never available on Windows and Python 2
	if hasattr(os, "fwalk") and not isinstance(directory, int):
		def auto_close_iter_fd(fd, iter):
			try:
				#PY2: Use `yield from` instead
				for item in iter:
					yield item
			finally:
				os.close(fd)

		directory_str = utils.convert_path(directory)
		dirname = os.path.basename(os.path.normpath(directory_str))

		fd = os.open(directory_str, os.O_CLOEXEC | os.O_DIRECTORY)
		body, headers = stream_directory_impl(fd, dirname)
		return auto_close_iter_fd(fd, body), headers
	else:
		return stream_directory_impl(directory)


def stream_filesystem_node(filepaths,
                           recursive=False, patterns='**',
                           chunk_size=default_chunk_size):
	"""Gets a buffered generator for streaming either files or directories.

	Returns a buffered generator which encodes the file or directory at the
	given path as :mimetype:`multipart/form-data` with the corresponding
	headers.

	Parameters
	----------
	filepaths : Union[str, bytes, os.PathLike, int, io.IOBase, collections.abc.Iterable]
		The filepath of a single directory or one or more files to stream
	recursive : bool
		Stream all content within the directory recursively?
	patterns : Union[str, re.compile, collections.abc.Iterable]
		Single *glob* pattern or list of *glob* patterns and compiled
		regular expressions to match the paths of files and directories
		to be added to IPFS (directories only)
	chunk_size : int
		Maximum size of each stream chunk
	"""
	is_dir = False
	if isinstance(filepaths, utils.path_types):
		is_dir = os.path.isdir(utils.convert_path(filepaths))
	elif isinstance(filepaths, int):
		import stat
		is_dir = stat.S_ISDIR(os.fstat(filepaths).st_mode)
	if is_dir:
		return stream_directory(filepaths, recursive, patterns, chunk_size) + (True,)
	else:
		return stream_files(filepaths, chunk_size) + (False,)


def stream_bytes(data, chunk_size=default_chunk_size):
	"""Gets a buffered generator for streaming binary data.

	Returns a buffered generator which encodes binary data as
	:mimetype:`multipart/form-data` with the corresponding headers.

	Parameters
	----------
	data : bytes
		The data bytes to stream
	chunk_size : int
		The maximum size of each stream chunk

	Returns
	-------
		(generator, dict)
	"""
	stream = BytesFileStream(data, chunk_size=chunk_size)
	return stream.body(), stream.headers()


def stream_text(text, chunk_size=default_chunk_size):
	"""Gets a buffered generator for streaming text.

	Returns a buffered generator which encodes a string as
	:mimetype:`multipart/form-data` with the corresponding headers.

	Parameters
	----------
	text : str
		The data bytes to stream
	chunk_size : int
		The maximum size of each stream chunk

	Returns
	-------
		(generator, dict)
	"""
	if inspect.isgenerator(text):
		def binary_stream():
			for item in text:
				if six.PY2 and isinstance(item, six.binary_type):
					#PY2: Allow binary strings under Python 2 since
					# Python 2 code is not expected to always get the
					# distinction between text and binary strings right.
					yield item
				else:
					yield item.encode("utf-8")
		data = binary_stream()
	elif six.PY2 and isinstance(text, six.binary_type):
		#PY2: See above.
		data = text
	else:
		data = text.encode("utf-8")

	return stream_bytes(data, chunk_size)
