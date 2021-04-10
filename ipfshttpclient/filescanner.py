import abc
import collections.abc
import enum
import fnmatch
import os
import re
import sys
import types
import typing as ty

from . import utils

# PyCharm rejects typing.AnyStr and will flag all usages of an error,
# effectively breaking PyCharm's ability to provide typing assistance.
#
# To encourage contributions from PyCharm users, we redefine AnyStr.
#
# This will get inlined if/when PyCharm no longer flags typing.AnyStr.
AnyStr = ty.TypeVar('AnyStr', bytes, str)

if sys.version_info >= (3, 7):  #PY37+
	re_pattern_type = re.Pattern
	if ty.TYPE_CHECKING:
		re_pattern_t = re.Pattern[AnyStr]
	else:
		re_pattern_t = re.Pattern
else:  #PY36-
	re_pattern_t = re_pattern_type = type(re.compile(""))


# Windows does not have os.O_DIRECTORY
O_DIRECTORY: int = getattr(os, "O_DIRECTORY", 0)


# Neither Windows nor MacOS have os.fwalk even through Python 3.9
HAVE_FWALK: bool = hasattr(os, "fwalk")
HAVE_FWALK_BYTES = HAVE_FWALK and sys.version_info >= (3, 7)


class Matcher(ty.Generic[AnyStr], metaclass=abc.ABCMeta):
	"""Represents a type that can match on file paths and decide whether they
	should be included in some file scanning/adding operation"""
	__slots__ = ("is_binary",)

	is_binary: bool

	def __init__(self, is_binary: bool = False) -> None:
		self.is_binary = is_binary
	
	@abc.abstractmethod
	def should_descend(self, path: AnyStr) -> bool:
		r"""Decides whether the file scanner should descend into the given directory path
		
		Arguments
		---------
		path
			A directory path upholding the same guarantees as those
			mentioned in :meth:`should_store`
		"""
	
	@abc.abstractmethod
	def should_report(self, path: AnyStr, *, is_dir: bool) -> bool:
		r"""Decides whether the file scanner should store the given file or directory
		
		Note that in this case “file” may refer to anything that is not a
		directory and not just regular files. If the settings of the file scanner
		do not permit it to follow symbolic links this may even include symbolic
		links pointing at directories.
		
		Arguments
		---------
		path
			The file or directory path to check – the argument's type depends on
			the type of the path originally passed to the file scanner and may
			either be :type:`bytes` or :type:`str`, but will usually be :type:`str`
			
			The given path is guaranteed to have the following additional properties:
			
			* It will be properly normalized: There won't be any empty (``…//…`),
			  single-dot (``…/./…``) or (``…/../…``) directory labels or leading
			  or trailing slashes.
			* Its path separator will match the one found in :var:`os.path.sep` –
			  that is: It will be \ on Windows and / everywhere else.
			* It will be relative to the file scanner's base directory.
		is_dir
			Whether the given path refers to a directory, see the above paragraph
			for what this means exactly
		"""


class MatchAll(ty.Generic[AnyStr], Matcher[AnyStr]):
	"""I want it all – I want it now…"""
	__slots__ = ()
	
	def should_descend(self, path: AnyStr) -> utils.Literal_True:
		return True
	
	def should_report(self, path: AnyStr, *, is_dir: bool) -> utils.Literal_True:
		return True


class MatchNone(ty.Generic[AnyStr], Matcher[AnyStr]):
	"""Fuck it"""
	__slots__ = ()
	
	def should_descend(self, path: AnyStr) -> utils.Literal_False:
		return False
	
	def should_report(self, path: AnyStr, *, is_dir: bool) -> utils.Literal_False:
		return False


class GlobMatcher(Matcher[AnyStr], ty.Generic[AnyStr]):
	"""Matches files and directories according to the shell glob conventions
	
	For details on the syntax see the Python :py:mod:`glob` module that this
	class emulates. If your are accustomed the globing on real Unix shells
	make sure to also carefully study its limitations as these also apply here.
	Also not that this matcher always has recursion enabled and hence treats
	``**``-labels as special. Additionally the *period_special* parameter is
	provided that may be used to disable the special handling of “dot-files”
	(files whose name starts with a leading period).
	
	One important thing to keep in mind that this is a *matcher* and works
	entirely I/O-less. As such, trying to include any files or directories
	*outside* of the matching domain will *not* work. For instance, a pattern
	like ``../a`` or ``b/../c`` would never match anything as a conforming
	file scanner would never pass in such a path, the same applies to any notion
	of absolute paths. This matcher will try its best to normalize or reject
	such cases, but if you're wondering why your pattern just won't match while
	pasting it into a real shell works this may be why.
	"""
	__slots__ = ("period_special", "_sep", "_pat", "_dir_only")

	period_special: bool

	_sep: AnyStr
	_pat: "ty.List[ty.Optional[re_pattern_t[AnyStr]]]"
	_dir_only: bool

	def __init__(self, pat: AnyStr, *, period_special: bool = True):
		"""
		Arguments
		---------
		pat
			The glob pattern to use for matching
		period_special
			Whether a leading period in file/directory names should be matchable by
			``*``, ``?`` and ``[…]`` – traditionally they are not, but many modern
			shells allow one to disable this behaviour
		"""
		super().__init__(isinstance(pat, bytes))

		self.period_special = period_special

		self._sep = utils.maybe_fsencode(os.path.sep, pat)
		dblstar = utils.maybe_fsencode("**", pat)
		dot = utils.maybe_fsencode(".", pat)
		pat_ndot = utils.maybe_fsencode(r"(?![.])", pat)

		# Normalize path separator
		if os.path.altsep:
			pat = pat.replace(utils.maybe_fsencode(os.path.altsep, pat), self._sep)
		
		# Sanity checks for stuff that will definitely NOT EVER match
		# (there is another one in the loop below)
		assert not os.path.isabs(pat), "Absolute matching patterns will never match"
		
		# Note the extra final slash for its effect of only matching directories
		#
		# (TBH, I find it hard to see how that is useful, but everybody does it
		#  and it keeps things consistent overall – something to only match files
		#  would be nice however.)
		self._dir_only = pat.endswith(self._sep)

		self._pat = []
		for label in pat.split(self._sep):
			# Skip over useless path components
			if len(label) < 1 or label == dot:
				continue
			
			assert label != dot + dot, 'Matching patterns containing ".." will never match'
			
			if label == dblstar:
				self._pat.append(None)
			elif dblstar in label:
				raise NotImplementedError(
					"Using double-star (**) and other characters in the same glob "
					"path label ({0}) is not currently supported – please do file "
					"an issue if you need this!".format(os.fsdecode(label))
				)
			else:
				if not isinstance(label, bytes):
					re_expr = fnmatch.translate(label)
				else:
					re_expr = fnmatch.translate(label.decode("latin-1")).encode("latin-1")
				
				if period_special and not label.startswith(dot):
					re_expr = pat_ndot + re_expr
				self._pat.append(re.compile(re_expr))

	def should_descend(self, path: AnyStr) -> bool:
		for idx, label in enumerate(path.split(self._sep)):
			# Always descend into any directory below a recursive pattern as we
			# cannot predict what we will later do a tail match on
			pattern = self._pat[idx]
			if pattern is None:
				return True
			
			# Do not descend further if we reached the last label of the pattern
			# (unless the final pattern label is a recursive match, see above)
			#
			# This is independent of whether this *directory* will be included
			# or not.
			if idx == (len(self._pat) - 1):
				return False
			
			# Match the current pattern to decide whether to keep looking or not
			if not pattern.match(label):
				return False
		
		# The given path matched part of this pattern, so we should include this
		# directory to go further
		return True

	def should_report(self, path: AnyStr, *, is_dir: bool) -> bool:
		# A final slash means “only match directories”
		if self._dir_only and not is_dir:
			return False
		
		labels = path.split(self._sep)

		return self._match(labels, idx_pat=0, idx_path=0, is_dir=is_dir)

	def _match(self, labels: ty.List[AnyStr], *, idx_pat: int, idx_path: int,
	           is_dir: bool) -> bool:
		while idx_pat < len(self._pat):
			pattern = self._pat[idx_pat]
			if pattern is None:
				break
			
			# Match initial labels before recursion
			if idx_path >= len(labels):
				# Pattern refers to something below this path, store it only if it
				# is a directory
				return is_dir
			elif not pattern.match(labels[idx_path]):
				# Pattern did not match
				return False
			
			idx_pat += 1
			idx_path += 1
		
		dot = utils.maybe_fsencode(".", labels[0])
		
		# We reached the end of the matching labels or the start of recursion
		if idx_pat == len(self._pat):
			# End of matching labels – only include path if it was of the same
			# length or the previous pattern label was recursive
			if self._pat[idx_pat - 1] is None:
				return not self.period_special or not labels[idx_path].startswith(dot)
			else:
				return idx_path == len(labels)
		
		# Start of recursion – move to next label and recurse this method too
		#
		# If the path is then matched by our inferior self return success,
		# otherwise retry with the next path label until all labels have been
		# exhausted meaning that there was no match.
		idx_pat += 1
		while idx_path < len(labels):
			if self._match(labels, idx_pat=idx_pat, idx_path=idx_path, is_dir=is_dir):
				return True
			
			# Do not add dot-files as part of recursive patterns by default
			if self.period_special and labels[idx_path].startswith(dot):
				break
			
			idx_path += 1
		
		# Nothing matched
		return False


class ReMatcher(Matcher[AnyStr], ty.Generic[AnyStr]):
	"""Matches files and directories using a regular expression pattern
	
	See the description of :meth:`Matcher.should_store` for the specifics on how
	the matching path is formatted, but note that there is one important
	difference: In order to allow the regular expression to distinguish between
	files and directories, all directories (if *is_dir* is ``True``) contain
	a trailing forward or backward slash (depending on the platform). If you
	don't care about the this information you may want to add ``[\\/]?`` to end
	of the pattern.
	
	Unlike glob patterns, regular expressions cannot be reliably analyzed for
	which directories the file paths they may or may not match are in. Because
	of this, this matcher will cause the file scanner **to recurse into any
	directory it encounters** possibly causing an unnecessarily slow-down during
	scanning even if only very few files end up being selected. If this causes
	problems for you *use non-recursive glob patterns instead* or implement your
	own matcher with a proper :meth:`Matcher.should_descend` method.
	"""
	__slots__ = ("_pat",)

	_pat: "re_pattern_t[AnyStr]"

	def __init__(self, pat: ty.Union[AnyStr, "re_pattern_t[AnyStr]"]):
		self._pat = re.compile(pat)

		super().__init__(not (self._pat.flags & re.UNICODE))
	
	def should_descend(self, path: AnyStr) -> bool:
		return True
	
	def should_report(self, path: AnyStr, *, is_dir: bool) -> bool:
		suffix: AnyStr = utils.maybe_fsencode(os.path.sep, path) if is_dir else type(path)()
		return bool(self._pat.match(path + suffix))


class MetaMatcher(Matcher[AnyStr], ty.Generic[AnyStr]):
	"""Match files and directories by delegating to other matchers"""
	__slots__ = ("_children",)

	_children: ty.List[Matcher[AnyStr]]

	def __init__(self, children: ty.List[Matcher[AnyStr]]):
		assert len(children) > 0
		super().__init__(children[0].is_binary)

		self._children = children

	def should_descend(self, path: AnyStr) -> bool:
		return any(m.should_descend(path) for m in self._children)
	
	def should_report(self, path: AnyStr, *, is_dir: bool) -> bool:
		return any(m.should_report(path, is_dir=is_dir) for m in self._children)


class NoRecusionAdapterMatcher(Matcher[AnyStr], ty.Generic[AnyStr]):
	"""Matcher adapter that will prevent any recursion
	
	Takes a subordinate matcher, but tells the scanner to never descend into any
	child directory and to never store files from such a directory. This is an
	effective way to prevent any non-top-level files from being emitted by the
	scanner and hence provides ``recursive=False`` semantics.
	"""
	__slots__ = ("_child",)

	_child: Matcher[AnyStr]

	def __init__(self, child: Matcher[AnyStr]):
		super().__init__(child.is_binary)

		self._child = child

	def should_descend(self, path: AnyStr) -> bool:
		return False
	
	def should_report(self, path: AnyStr, *, is_dir: bool) -> bool:
		return utils.maybe_fsencode(os.path.sep, path) not in path \
		       and self._child.should_report(path, is_dir=is_dir)


if ty.TYPE_CHECKING:
	_match_spec_t = ty.Union[AnyStr, re_pattern_t[AnyStr], Matcher[AnyStr]]
else:
	# Using `re_pattern_t` here like in the type checking case makes
	# sphinx_autodoc_typehints explode
	_match_spec_t = ty.Union[AnyStr, re_pattern_t, Matcher[AnyStr]]
match_spec_t = ty.Union[
	ty.Iterable[_match_spec_t[AnyStr]],
	_match_spec_t[AnyStr]
]


class MatcherSpecInvalidError(TypeError):
	def __init__(self, invalid_spec: ty.Any) -> None:
		super().__init__(
			f"Don't know how to create a {Matcher.__name__} from spec {invalid_spec!r}"
		)


def _require_spec(spec: ty.Optional[match_spec_t[AnyStr]]) -> match_spec_t[AnyStr]:
	"""
	Assist the type checker by narrowing the number of places accepting Optional.
	"""

	if spec is None:
		return MatchAll()
	else:
		return spec


@ty.overload
def matcher_from_spec(spec: match_spec_t[bytes], *,
                      period_special: bool = ...,
                      recursive: bool = ...) -> Matcher[bytes]:
	...


@ty.overload
def matcher_from_spec(spec: match_spec_t[str], *,
                      period_special: bool = ...,
                      recursive: bool = ...) -> Matcher[str]:
	...


@ty.overload  # noqa: E302
def matcher_from_spec(spec: None, *,
                      period_special: bool = ...,
                      recursive: bool = ...) -> Matcher[str]:
	...


def matcher_from_spec(spec: ty.Optional[match_spec_t[AnyStr]], *,  # noqa: E302
                      period_special: bool = True,
                      recursive: bool = True) -> Matcher[AnyStr]:
	"""Processes the given simplified matching spec, creating an equivalent :type:`Matcher` object"""

	return _matcher_from_spec(
		_require_spec(spec),
		period_special=period_special,
		recursive=recursive
	)


def _matcher_from_spec(spec: match_spec_t[AnyStr], *,  # noqa: E302
                       period_special: bool = True,
                       recursive: bool = True) -> Matcher[AnyStr]:
	if recursive:
		return _recursive_matcher_from_spec(spec, period_special=period_special)
	else:
		guarded = matcher_from_spec(
			spec,
			recursive=True,
			period_special=period_special
		)

		return NoRecusionAdapterMatcher(guarded)


def _recursive_matcher_from_spec(spec: match_spec_t[AnyStr], *,  # noqa: E302
                                 period_special: bool = True) -> Matcher[AnyStr]:
	if isinstance(spec, re_pattern_type):
		return ReMatcher(spec)
	elif isinstance(spec, (str, bytes)):
		return GlobMatcher(spec, period_special=period_special)
	elif isinstance(spec, Matcher):
		return spec
	elif isinstance(spec, collections.abc.Iterable):
		matchers: ty.List[Matcher[AnyStr]] = [
			_recursive_matcher_from_spec(
				ty.cast(match_spec_t[AnyStr], s),
				period_special=period_special)
			for s in spec
		]

		if len(matchers) == 0:  # Edge case: Empty list of matchers
			return MatchNone()
		elif len(matchers) == 1:  # Edge case: List of exactly one matcher
			return matchers[0]
		else:  # Actual list of matchers (plural)
			return MetaMatcher(matchers)
	else:
		raise MatcherSpecInvalidError(spec)


if ty.TYPE_CHECKING:
	from .filescanner_ty import FSNodeType, FSNodeEntry
else:
	class FSNodeType(enum.Enum):
		FILE = enum.auto()
		DIRECTORY = enum.auto()
	
	FSNodeEntry = ty.NamedTuple("FSNodeEntry", [
		("type", FSNodeType),
		("path", AnyStr),
		("relpath", AnyStr),
		("name", AnyStr),
		("parentfd", ty.Optional[int])
	])


class walk(ty.Generator[FSNodeEntry, ty.Any, None], ty.Generic[AnyStr]):
	__slots__ = ("_generator", "_close_fd")

	_generator: ty.Generator[FSNodeEntry, None, None]
	_close_fd: ty.Optional[int]

	def __init__(
			self,
			directory: ty.Union[AnyStr, utils.PathLike[AnyStr], int],
			match_spec: ty.Optional[match_spec_t[AnyStr]] = None, *,
			follow_symlinks: bool = False,
			intermediate_dirs: bool = True,
			period_special: bool = True,
			recursive: bool = True
	) -> None:
		"""
		Arguments
		---------
		directory
			Path to, or file descriptor of, directory to scan
		match_spec
			Matching rules for limiting the files and directories to include in
			the scan
			
			By default everything will be scanned and included.
		follow_symlinks
			Follow symbolic links while scanning?
		period_special
			The value to pass to the *period_special* argument of :class:`GlobMatcher`
			when constructing such an object from the given *match_spec*
		intermediate_dirs
			When reporting a file or directory first ensure that all containing
			directories were already reported
			
			Due to the way matching works, a matcher may only ask for its target
			files to be included but not care about the directories leading up
			to that file and this would cause the file to be reported without
			these intermediate directories to the caller as well. If you require
			these directories to be reported for consistency, this option will
			keep track of these intermediate paths and make it appear as if these
			had been included up-front.
		recursive
			Recurse into the given directory while scanning?
			
			If ``False`` this will wrap the given matcher inside
			:class:`NoRecusionAdapterMatcher` and hence prevent the scanner from
			doing any recursion.
		"""
		self._close_fd = None

		# Create matcher object
		matcher: Matcher[AnyStr] = _matcher_from_spec(
			_require_spec(match_spec),
			recursive=recursive,
			period_special=period_special
		)

		# Convert directory path to string …
		if isinstance(directory, int):
			if not HAVE_FWALK:
				raise NotImplementedError("Passing a file descriptor as directory is "
				                          "not supported on this platform")

			self._generator = self._walk(
				directory,
				None,
				matcher,  # type: ignore[arg-type]
				follow_symlinks,
				intermediate_dirs
			)
		else:
			directory_str = os.fspath(directory)

			# Best-effort ensure that target directory exists if it is accessed by path
			os.stat(directory_str)
			
			# … and possibly open it as a FD if this is supported by the platform
			#
			# Note: `os.fwalk` support for binary paths was only added in 3.7+.
			directory_str_or_fd: ty.Union[AnyStr, int] = directory_str
			if HAVE_FWALK and (not isinstance(directory_str, bytes) or HAVE_FWALK_BYTES):
				fd = os.open(directory_str, os.O_RDONLY | O_DIRECTORY)
				self._close_fd = directory_str_or_fd = fd

			self._generator = self._walk(
				directory_str_or_fd,
				directory_str,
				matcher,  # type: ignore[arg-type]
				follow_symlinks,
				intermediate_dirs
			)

	def __iter__(self) -> 'walk[AnyStr]':
		return self
	
	def __next__(self) -> FSNodeEntry:
		return next(self._generator)
	
	def __enter__(self) -> 'walk[AnyStr]':
		return self
	
	def __exit__(self, *a: ty.Any) -> None:
		self.close()
	
	def send(self, value: ty.Any) -> FSNodeEntry:
		return self._generator.send(value)
	
	@ty.overload
	def throw(self, typ: ty.Type[BaseException],  # noqa: E704
	          val: ty.Union[BaseException, object] = ...,
	          tb: ty.Optional[types.TracebackType] = ...) -> FSNodeEntry: ...
	
	@ty.overload
	def throw(self, typ: BaseException, val: None = ...,  # noqa: E704
	          tb: ty.Optional[types.TracebackType] = ...) -> FSNodeEntry: ...
	
	def throw(self, typ: ty.Union[ty.Type[BaseException], BaseException],
	          val: ty.Union[BaseException, object] = None,
	          tb: ty.Optional[types.TracebackType] = None) -> FSNodeEntry:
		try:
			if isinstance(typ, type):
				bt = ty.cast(ty.Type[BaseException], typ)  # type: ignore[redundant-cast]
				return self._generator.throw(bt, val, tb)
			else:
				assert val is None
				return self._generator.throw(typ, val, tb)
		except:
			if self._close_fd is not None:
				os.close(self._close_fd)
				self._close_fd = None
			raise
	
	def close(self) -> None:
		try:
			self.throw(GeneratorExit)
		except GeneratorExit:
			pass
	
	@staticmethod
	def _join_dirs_and_files(dirnames: ty.List[AnyStr], filenames: ty.List[AnyStr]) \
	    -> ty.Iterator[ty.Tuple[AnyStr, bool]]:
		for dirname in dirnames:
			yield (dirname, True)
		
		for filename in filenames:
			yield (filename, False)
	
	def _walk(
			self,
			directory: ty.Union[AnyStr, int],
			directory_str: ty.Optional[AnyStr],
			matcher: Matcher[AnyStr],
			follow_symlinks: bool,
			intermediate_dirs: bool
	) -> ty.Generator[FSNodeEntry, ty.Any, None]:
		if directory_str is not None:
			sep = utils.maybe_fsencode(os.path.sep, directory_str)
		elif matcher is not None and matcher.is_binary:
			sep = os.fsencode(os.path.sep)  # type: ignore[assignment]
		else:
			sep = os.path.sep  # type: ignore[assignment]
		dot = utils.maybe_fsencode(".", sep)
		
		# Identify the leading portion of the `dirpath` returned by `os.walk`
		# that should be dropped
		if not isinstance(directory, int):
			while directory.endswith(sep):
				directory = directory[:-len(sep)]
		prefix = (directory if not isinstance(directory, int) else dot) + sep

		reported_directories: ty.Set[AnyStr] = set()
		
		# Always report the top-level directory even if nothing therein is matched
		reported_directories.add(utils.maybe_fsencode("", sep))
		yield FSNodeEntry(  # type: ignore[misc]  # mypy bug: gh/python/mypy#685
			type     = FSNodeType.DIRECTORY,
			path     = prefix[:-len(sep)],  # type: ignore[arg-type]
			relpath  = dot,  # type: ignore[arg-type]
			name     = dot,  # type: ignore[arg-type]
			parentfd = None
		)
		
		if not isinstance(directory, int):
			walk_iter = os.walk(directory, followlinks=follow_symlinks
			)  # type: ty.Union[ty.Iterator[ty.Tuple[AnyStr, ty.List[AnyStr], ty.List[AnyStr], int]], ty.Iterator[ty.Tuple[AnyStr, ty.List[AnyStr], ty.List[AnyStr]]]]  # noqa: E501
		else:
			walk_iter = os.fwalk(dot, dir_fd=directory, follow_symlinks=follow_symlinks)
		try:
			for result in walk_iter:
				dirpath, dirnames, filenames = result[0:3]

				if len(result) <= 3:
					dirfd: ty.Optional[int] = None
				else:
					# mypy wrongly believes this will produce an index-out-of-range exception.
					dirfd = result[3]  # type: ignore[misc]

				# Remove the directory prefix from the received path
				_, _, dirpath = dirpath.partition(prefix)
				
				# Keep track of reported intermediaries, so that we only check for
				# these at most once per directory base
				intermediates_reported = False
				
				for filename, is_dir in self._join_dirs_and_files(list(dirnames), filenames):
					filepath = os.path.join(dirpath, filename)
					
					# Check if matcher thinks we should descend into this directory
					if is_dir and not matcher.should_descend(filepath):
						dirnames.remove(filename)
					
					# Check if matcher thinks we should report this node
					if not matcher.should_report(filepath, is_dir=is_dir):
						continue
					
					# Ensure that all containing directories are reported
					# before reporting this node
					if not intermediates_reported and intermediate_dirs:
						parts = dirpath.split(sep)
						for end_offset in range(len(parts)):
							parent_dirpath = sep.join(parts[0:(end_offset + 1)])
							if parent_dirpath not in reported_directories:
								reported_directories.add(parent_dirpath)
								yield FSNodeEntry(  # type: ignore[misc]  # mypy bug: gh/python/mypy#685
									type     = FSNodeType.DIRECTORY,
									path     = (prefix + parent_dirpath),  # type: ignore[arg-type]
									relpath  = parent_dirpath,  # type: ignore[arg-type]
									name     = parts[end_offset],  # type: ignore[arg-type]
									parentfd = None
								)
						intermediates_reported = True
					
					# Report the target file or directory
					if is_dir:
						reported_directories.add(filepath)
						yield FSNodeEntry(  # type: ignore[misc]  # mypy bug: gh/python/mypy#685
							type     = FSNodeType.DIRECTORY,
							path     = (prefix + filepath),  # type: ignore[arg-type]
							relpath  = filepath,  # type: ignore[arg-type]
							name     = filename,  # type: ignore[arg-type]
							parentfd = dirfd
						)
					else:
						yield FSNodeEntry(  # type: ignore[misc]  # mypy bug: gh/python/mypy#685
							type     = FSNodeType.FILE,
							path     = (prefix + filepath),  # type: ignore[arg-type]
							relpath  = filepath,  # type: ignore[arg-type]
							name     = filename,  # type: ignore[arg-type]
							parentfd = dirfd
						)
		finally:
			# Make sure the file descriptors bound by `os.fwalk` are freed on error
			walk_iter.close()  # type: ignore[union-attr]  # typeshed bug
			
			# Close root file descriptor of `os.fwalk` as well
			if self._close_fd is not None:
				os.close(self._close_fd)
				self._close_fd = None


if HAVE_FWALK:  # pragma: no cover
	supports_fd: ty.FrozenSet[ty.Callable[..., ty.Any]] = frozenset({walk})
else:  # pragma: no cover
	supports_fd = frozenset()
