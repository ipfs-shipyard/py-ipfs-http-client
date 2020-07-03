#!/usr/bin/python

import contextlib
import itertools
import locale
import os
import pathlib
import random
import shutil
import subprocess
import sys
import tempfile

import pytest


if not hasattr(contextlib, "suppress"):
	"""
	Polyfill for ``contextlib.suppress``
	"""
	@contextlib.contextmanager
	def _contextlib_suppress(*exceptions):
		try:
			yield
		except exceptions:
			pass
	contextlib.suppress = _contextlib_suppress


######################
# Test configuration #
######################

# Environment name as used by `tox`
ENVNAME = "py{}{}".format(sys.version_info.major, sys.version_info.minor)

# Determine project base directory and testing path
BASE_PATH = pathlib.Path(__file__).parent.parent
TEST_PATH = BASE_PATH / "build" / "test-{}".format(ENVNAME)
IPFS_PATH = TEST_PATH / "ipfs-path"

ADDR = "/ip4/127.0.0.1/tcp/{0}".format(random.randrange(40000, 65535))


###########################
# Set up test environment #
###########################

# Add project directory to PYTHONPATH
sys.path.insert(0, str(BASE_PATH))

# Switch working directory to project directory
os.chdir(str(BASE_PATH))

# Export environment variables required for testing
os.environ["IPFS_PATH"] = str(IPFS_PATH)
os.environ["PY_IPFS_HTTP_CLIENT_DEFAULT_ADDR"] = str(ADDR)

# Make sure the IPFS data directory exists and is empty
with contextlib.suppress(FileNotFoundError):
	shutil.rmtree(str(IPFS_PATH))

with contextlib.suppress(FileExistsError):
	os.makedirs(str(IPFS_PATH))

# Initialize the IPFS data directory
subprocess.call(["ipfs", "init"])
subprocess.call(["ipfs", "config", "Addresses.Gateway", ""])
subprocess.call(["ipfs", "config", "Addresses.API",     ADDR])
subprocess.call(["ipfs", "config", "--bool", "Experimental.FilestoreEnabled", "true"])


################
# Start daemon #
################

extra_args = {}
if sys.version_info >= (3, 6, 0):
	extra_args["encoding"] = locale.getpreferredencoding()
else:  #PY35: `subprocess.Popen` encoding parameter missing
	extra_args["universal_newlines"] = True

# Spawn IPFS daemon in data directory
print("Starting IPFS daemon on {0}…".format(ADDR), file=sys.stderr)
DAEMON = subprocess.Popen(
	["ipfs", "daemon", "--enable-pubsub-experiment"],
	stdout=subprocess.PIPE,
	stderr=subprocess.STDOUT,
	**extra_args
)


class DaemonProcessPlugin:
	"""Tiny pytest plugin to inject daemon object reference as test “fixture” value."""
	@pytest.hookimpl(hookwrapper=True)
	def pytest_pyfunc_call(self, pyfuncitem):
		if "daemon" in pyfuncitem.funcargs:
			pyfuncitem.funcargs["daemon"] = DAEMON
		yield


# Wait for daemon to start up
for line in DAEMON.stdout:
	print("\t{0}".format(line), end="", file=sys.stderr)
	if line.strip() == "Daemon is ready":
		break

#XXX: This design could deadlock the test run if the daemon were to produce more
#     output than fits into its output pipe before shutdown


##################
# Run test suite #
##################

PYTEST_CODE = 1
try:
	# Make sure all required pytest plugins are loaded up-front
	os.environ["PYTEST_PLUGINS"] = ",".join([
		"cid",
		"dependency",
		"localserver",
		"pytest_cov",
		"pytest_mock",
		"pytest_ordering",
	])
	
	with tempfile.NamedTemporaryFile("r+") as coveragerc:
		coverage_args = []
		if os.name != "nt":
			PREFER_HTTPX = (os.environ.get("PY_IPFS_HTTP_CLIENT_PREFER_HTTPX", "no").lower()
			                not in ("0", "f", "false", "n", "no"))
			
			# Assemble list of files to exclude from coverage analysis
			omitted_files = [
				"ipfshttpclient/requests_wrapper.py",
			]
			if PREFER_HTTPX and sys.version_info >= (3, 6):
				omitted_files.append("ipfshttpclient/http_requests.py")
			else:  #PY35: Fallback to old requests-based code instead of HTTPX
				omitted_files.append("ipfshttpclient/http_httpx.py")
			
			# Assemble list of coverage data exclusion patterns (also escape the
			# hash sign [#] as it has a special meaning [comment] in the generated
			# configuration file)
			exclusions = [
				# Add the standard coverage exclusion statement
				r"pragma:\s+no\s+cover",
				
				# Ignore typing-only branches
				r"if\s+(?:[A-Za-z]+\s*[.]\s*)?TYPE_CHECKING\s*:",
				
				# Ignore dummy ellipsis expression line
				r"^\s*\.\.\.\s*$",
			]
			if sys.version_info.major == 2:
				exclusions.append(r"\#PY3")
			else:
				# Exclude the past
				exclusions.append(r"\#PY2")
				# Exclude code only used for compatiblity with a previous Python version
				exclusions.append(r"\#PY3({0})([^\d+]|$)".format(
					"|".join(map(str, range(0, sys.version_info.minor)))
				))
				# Exclude code only used in future Python versions
				exclusions.append(r"\#PY3({0})\+".format(
					"|".join(map(str, range(sys.version_info.minor + 1, 20)))
				))
			
			if PREFER_HTTPX and sys.version_info >= (3, 6):
				exclusions.append(r"\# pragma: http-backend=requests")
			else:  #PY35: Fallback to old requests-based code instead of HTTPX
				exclusions.append(r"\# pragma: http-backend=httpx")
			
			# Create temporary file with extended *coverage.py* configuration data
			coveragerc.file.writelines(map(lambda s: s + "\n", itertools.chain((
				"[run]",
				"omit =",
			), map(lambda s: "\t" + s, omitted_files),
			(
				"[report]",
				"# Exclude lines specific to some other Python version from coverage",
				"exclude_lines =",
			), map(lambda s: "\t" + s, exclusions))))
			coveragerc.file.flush()
			
			coverage_args = [
				"--cov=ipfshttpclient",
				"--cov-branch",
				"--cov-config={0}".format(coveragerc.name),
				"--no-cov-on-fail",
				"--cov-fail-under=90",
				"--cov-report=term",
				"--cov-report=html:{}".format(str(TEST_PATH / "cov_html")),
				"--cov-report=xml:{}".format(str(TEST_PATH / "cov.xml")),
			]
		
		# Launch pytest in-process
		PYTEST_CODE = pytest.main([
			"--verbose",
		] + coverage_args + sys.argv[1:], plugins=[DaemonProcessPlugin()])
finally:
	try:
		# Move coverage file to test directory (so that the coverage files of different
		# versions can be merged later on)
		shutil.move(str(BASE_PATH / ".coverage"), str(TEST_PATH / "cov_raw"))
	except FileNotFoundError:
		pass  # Early crash in pytest or Windows – no coverage data generated
	
	# Make sure daemon was terminated during the tests
	if DAEMON.poll() is None:  # "if DAEMON is running"
		DAEMON.kill()
		
		print("IPFS daemon was still running after test!", file=sys.stderr)
	
	output = list(DAEMON.stdout)
	if output:
		print("IPFS daemon printed extra messages:", file=sys.stderr)
		for line in output:
			print("\t{0}".format(line), end="", file=sys.stderr)

sys.exit(PYTEST_CODE)
