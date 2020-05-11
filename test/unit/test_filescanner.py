import os.path
import re
import sys
import typing as ty

import pytest

from ipfshttpclient import filescanner


TEST_FILE_DIR = os.path.join(os.path.dirname(__file__), "..", "functional")  # type: str


@pytest.mark.skipif(sys.version_info < (3, 6), reason="fnmatch.translate output changed in Python 3.6+")
@pytest.mark.parametrize("pattern,expected,kwargs", [
	("literal",                  [r"(?![.])(?s:literal)\Z"], {}),
	(b"literal",                 [br"(?![.])(?s:literal)\Z"], {}),
	("*.a",                      [r"(?![.])(?s:.*\.a)\Z"], {}),
	(b"*.a",                     [br"(?![.])(?s:.*\.a)\Z"], {}),
	("*/**/*.dir/**/**/.hidden", [r"(?![.])(?s:.*)\Z", None, r"(?![.])(?s:.*\.dir)\Z", None, None, r"(?s:\.hidden)\Z"], {}),
	("*/**/*.dir/**/**/.hidden", [r"(?s:.*)\Z", None, r"(?s:.*\.dir)\Z", None, None, r"(?s:\.hidden)\Z"], {"period_special": False}),
	("././/////////./*.a",       [r"(?![.])(?s:.*\.a)\Z"], {}),
	(b"././/////////./*.a",      [br"(?![.])(?s:.*\.a)\Z"], {}),
	("*/*.a",                    [r"(?![.])(?s:.*)\Z", r"(?![.])(?s:.*\.a)\Z"], {}),
	("*/*.a",                    [r"(?s:.*)\Z", r"(?s:.*\.a)\Z"], {"period_special": False}),
])
def test_glob_compile(pattern: ty.AnyStr, expected: ty.List[ty.AnyStr], kwargs: ty.Dict[str, bool]):
	matcher = filescanner.GlobMatcher(pattern, **kwargs)
	assert list(map(lambda r: r.pattern if r is not None else None, matcher._pat)) == expected


def test_glob_sep_normalize(monkeypatch):
	monkeypatch.setattr(os.path, "sep", "#")
	monkeypatch.setattr(os.path, "altsep", "~")
	
	assert len(filescanner.GlobMatcher("a#b~c")._pat) == 3
	
	monkeypatch.setattr(os.path, "altsep", None)
	
	assert len(filescanner.GlobMatcher("a#b~c")._pat) == 2


# Possible hypothesis test: Parsing glob should never fail, except in the following 3 cases.

@pytest.mark.skipif(sys.flags.optimize, reason="Glob error asserts are stripped from optimized code")
@pytest.mark.parametrize("pattern", [
	"../*",
	b"../*",
	"/absolute/file/path",
	b"/absolute/file/path",
])
def test_glob_errors(pattern):
	with pytest.raises(AssertionError):
		filescanner.GlobMatcher(pattern)


def test_glob_not_implemented():
	with pytest.raises(NotImplementedError):
		filescanner.GlobMatcher("*/.**")


@pytest.mark.parametrize("pattern,path,is_dir,descend,report,kwargs", [
	# Basic literal path tests
	("literal",  "other",         False, False, False, {}),
	("literal",  "literal",       False, False, True,  {}),
	("literal",  "literal/more",  False, False, False, {}),
	(b"literal", b"other",        False, False, False, {}),
	(b"literal", b"literal",      False, False, True,  {}),
	(b"literal", b"literal/more", False, False, False, {}),
	("literal/more",  "other",         False, False, False, {}),
	("literal/more",  "literal",       False, True,  False, {}),
	("literal/more",  "literal",       True,  True,  True,  {}),
	("literal/more",  "literal/more",  False, False, True,  {}),
	(b"literal/more", b"other",        False, False, False, {}),
	(b"literal/more", b"literal",      False, True,  False, {}),
	(b"literal/more", b"literal",      True,  True,  True,  {}),
	(b"literal/more", b"literal/more", False, False, True,  {}),
	("literal/more",  "other",         False, False, False, {"recursive": False}),
	("literal/more",  "literal",       False, False, False, {"recursive": False}),
	("literal/more",  "literal",       True,  False, True,  {"recursive": False}),
	("literal/more",  "literal/more",  False, False, False, {"recursive": False}),
	
	# Test basic leading-period handling
	("*.a", ".a", False, False, False, {}),
	("*.a", ".a", False, False, True,  {"period_special": False}),
	("*.a", ".a", True,  False, False, {}),
	("*.a", ".a", True,  False, True,  {"period_special": False}),
	
	# Test leading-period with trailing slash handling
	("*.a/", ".a", False, False, False, {}),
	("*.a/", ".a", False, False, False, {"period_special": False}),
	("*.a/", ".a", True,  False, False, {}),
	("*.a/", ".a", True,  False, True,  {"period_special": False}),
	
	# Tests for double-star recursion with premium leading-period shenanigans
	("*/**/*.dir/**/**/.hidden", ".dir/.hidden",                  False, False, False, {}),
	("*/**/*.dir/**/**/.hidden", "a/.dir/.hidden",                False, True,  False, {}),
	("*/**/*.dir/**/**/.hidden", "a/b.dir/.hidden",               False, True,  True,  {}),
	("*/**/*.dir/**/**/.hidden", "a/u/v/w/b.dir/c/d/e/f/.hidden", False, True,  True,  {}),
	("**", ".a", False, True, False, {}),
	(filescanner.GlobMatcher("**"), ".a", False, True, False, {}),
	
	# Regular expression test
	(re.compile(r"[^/\\]+[/\\](IMG-\d{0,4}\.jpeg)?$"),  "Camera/IMG-0169.jpeg",  False, True, True,  {}),
	(re.compile(r"[^/\\]+[/\\](IMG-\d{0,4}\.jpeg)?$"),  "Camera",                True,  True, True,  {}),
	(re.compile(r"[^/\\]+[/\\](IMG-\d{0,4}\.jpeg)?$"),  "Camera/Thumbs.db",      False, True, False, {}),
	(re.compile(br"[^/\\]+[/\\](IMG-\d{0,4}\.jpeg)?$"), b"Camera/IMG-0169.jpeg", False, True, True,  {}),
	(re.compile(br"[^/\\]+[/\\](IMG-\d{0,4}\.jpeg)?$"), b"Camera",               True,  True, True,  {}),
	(re.compile(br"[^/\\]+[/\\](IMG-\d{0,4}\.jpeg)?$"), b"Camera/Thumbs.db",     False, True, False, {}),
	(filescanner.ReMatcher(br"[^/\\]+[/\\](IMG-\d{0,4}\.jpeg)?$"), b"Camera/Thumbs.db",     False, True, False, {}),
	
	# Multiple patterns
	(["*/**/*.dir/**/**/.hidden",  re.compile(r"[^/\\]+[/\\](IMG-\d{0,4}\.jpeg)?$")],  "Camera/IMG-1279.jpeg",  False, True, True,  {}),
	([b"*/**/*.dir/**/**/.hidden", re.compile(br"[^/\\]+[/\\](IMG-\d{0,4}\.jpeg)?$")], b"Camera/IMG-1279.jpeg", False, True, True,  {}),
	(["*/**/*.dir/**/**/.hidden",  re.compile(r"[^/\\]+[/\\](IMG-\d{0,4}\.jpeg)?$")],  "a/.dir/.hidden",        False, True, False, {}),
	([b"*/**/*.dir/**/**/.hidden", re.compile(br"[^/\\]+[/\\](IMG-\d{0,4}\.jpeg)?$")], b"a/.dir/.hidden",       False, True, False, {}),
	(["*/**/*.dir/**/**/.hidden",  re.compile(r"[^/\\]+[/\\](IMG-\d{0,4}\.jpeg)?$")],  "a/b.dir/.hidden",       False, True, True,  {}),
	([b"*/**/*.dir/**/**/.hidden", re.compile(br"[^/\\]+[/\\](IMG-\d{0,4}\.jpeg)?$")], b"a/b.dir/.hidden",      False, True, True,  {}),
	
	# Edge case: No patterns
	([], "???",  False, False, False, {}),
	([], b"???", False, False, False, {}),
])
def test_glob_matching(
		monkeypatch,
		pattern: ty.Union[ty.AnyStr, filescanner.re_pattern_t, ty.List[ty.Union[ty.AnyStr, filescanner.re_pattern_t]]],
		path: ty.AnyStr,
		is_dir: bool,
		descend: bool,
		report: bool,
		kwargs: ty.Dict[str, bool]
):
	# Hopefully useless sanity check
	assert os.path.sep == "/" or os.path.altsep == "/"
	
	slash = "/"         if isinstance(path, str) else b"/"  # type: ty.AnyStr
	sep   = os.path.sep if isinstance(path, str) else os.fsencode(os.path.sep)  # type: ty.AnyStr
	
	path = path.replace(slash, sep)
	
	matcher = filescanner.matcher_from_spec(pattern, **kwargs)
	assert matcher.should_descend(path)               is descend
	assert matcher.should_report(path, is_dir=is_dir) is report


def test_walk_fd_unsupported(monkeypatch):
	monkeypatch.setattr(filescanner, "HAVE_FWALK", False)
	
	with pytest.raises(NotImplementedError):
		filescanner.walk(0)


def test_walk_instaclose(mocker):
	close_spy = mocker.spy(filescanner.walk, "close")
	
	with filescanner.walk("."):
		pass
	
	close_spy.assert_called_once()


@pytest.mark.parametrize("path,pattern,kwargs,expected", [
	(TEST_FILE_DIR + os.path.sep + "fake_dir_almost_empty" + os.path.sep, None, {}, [
		(filescanner.FSNodeType.DIRECTORY, ".", "."),
		(filescanner.FSNodeType.FILE, ".gitignore", ".gitignore"),
	]),
	(TEST_FILE_DIR + os.path.sep + "fake_dir", ["test2", "test3"], {}, [
		(filescanner.FSNodeType.DIRECTORY, ".", "."),
		(filescanner.FSNodeType.DIRECTORY, "test2", "test2"),
		(filescanner.FSNodeType.DIRECTORY, "test3", "test3"),
	]),
])
def test_walk(monkeypatch, path: str, pattern: None, kwargs: ty.Dict[str, bool], expected: ty.List[filescanner.FSNodeEntry]):
	result = [(e.type, e.relpath, e.name) for e in filescanner.walk(path, pattern, **kwargs)]
	assert sorted(result, key=lambda r: r[1]) == expected
	
	# Check again with plain `os.walk` if the current platform supports `os.fwalk`
	if filescanner.HAVE_FWALK:
		monkeypatch.setattr(filescanner, "HAVE_FWALK", False)
		
		result = [(e.type, e.relpath, e.name) for e in filescanner.walk(path, pattern, **kwargs)]
		assert sorted(result, key=lambda r: r[1]) == expected


def test_supports_fd():
	assert (filescanner.walk in filescanner.supports_fd) is filescanner.HAVE_FWALK
