#!/usr/bin/python
# -*- encoding: utf-8 -*-
from __future__ import print_function

import contextlib
import locale
import pathlib
import os
import random
import shutil
import subprocess
import sys


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
with contextlib.suppress(OSError):  #PY2: Replace with `FileNotFoundError`
	shutil.rmtree(str(IPFS_PATH))

with contextlib.suppress(OSError):  #PY2: Replace with `FileExistsError`
	os.makedirs(str(IPFS_PATH))

# Initialize the IPFS data directory
subprocess.call(["ipfs", "init"])
subprocess.call(["ipfs", "config", "Addresses.Gateway", ""])
subprocess.call(["ipfs", "config", "Addresses.API",     ADDR])
subprocess.call(["ipfs", "config", "--bool", "Experimental.FilestoreEnabled", "true"])


################
# Start daemon #
################

#PY2: Only add `encoding` parameter on Python 3 as it's not available on Unicode-hostile versions
extra_args = {}
if sys.version_info >= (3, 6, 0):
	extra_args["encoding"] = locale.getpreferredencoding()
elif sys.version_info >= (3, 0, 0):  #PY35: `subprocess.Popen` encoding parameter missing
	extra_args["universal_newlines"] = True

# Spawn IPFS daemon in data directory
print("Starting IPFS daemon on {0}…".format(ADDR), file=sys.stderr)
DAEMON = subprocess.Popen(
	["ipfs", "daemon", "--enable-pubsub-experiment"],
	stdout=subprocess.PIPE,
	stderr=subprocess.STDOUT,
	**extra_args
)
os.environ["PY_IPFS_HTTP_CLIENT_TEST_DAEMON_PID"] = str(DAEMON.pid)

# Collect the exit code of `DAEMON` when `SIGCHLD` is received
# (otherwise the shutdown test fails to recognize that the daemon process is dead)
if os.name == "posix":
	import signal
	signal.signal(signal.SIGCHLD, lambda *a: DAEMON.poll())

# Wait for daemon to start up
#PY2: Using `for line in DAEMON.stdout` hangs the process
line = DAEMON.stdout.readline()
while line is not None:
	print("\t{0}".format(line), end="", file=sys.stderr)
	if line.strip() == "Daemon is ready":
		break
	line = DAEMON.stdout.readline()

#XXX: This design will deadlock the test run if the daemon were to produce more output than fits
#     into its output pipe before shutdown


##################
# Run test suite #
##################

PYTEST_CODE = 1
try:
	# Run tests in CI-mode (will stop the daemon at the end through the API)
	os.environ["CI"] = "true"
	
	# Make sure all required py.test plugins are loaded
	os.environ["PYTEST_PLUGINS"] = ",".join(["pytest_cov", "pytest_ordering"])
	
	# Launch py.test in-process
	import pytest
	PYTEST_CODE = pytest.main([
		"--verbose",
		"--cov=ipfshttpclient",
		"--cov-report=term",
		"--cov-report=html:{}".format(str(TEST_PATH / "cov_html")),
		"--cov-report=xml:{}".format(str(TEST_PATH / "cov.xml"))
	] + sys.argv[1:])
finally:
	# Move coverage file to test directory (so that the coverage files of different
	# versions can be merged later on)
	shutil.move(str(BASE_PATH / ".coverage"), str(TEST_PATH / "cov_raw"))
	
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
