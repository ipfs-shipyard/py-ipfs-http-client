# _*_ coding: utf-8 -*-
import os
import time

import pytest



def test_version(client):
	expected_keys = {"Repo", "Commit", "Version"}
	resp_version = client.version()
	assert set(resp_version.keys()).issuperset(expected_keys)


def test_id(client):
	expected_keys = {"PublicKey", "ProtocolVersion", "ID", "AgentVersion", "Addresses"}
	resp_id = client.id()
	assert set(resp_id.keys()).issuperset(expected_keys)


#################
# Shutdown test #
#################

def check_pid_exists(pid):
	"""
	Check whether pid exists in the current process table

	Source: https://stackoverflow.com/a/23409343/277882
	"""
	if os.name == "posix":
		import errno
		if pid < 0:
			return False
		try:
			os.kill(pid, 0)
		except OSError as e:
			return e.errno == errno.EPERM
		else:
			return True
	else:
		import ctypes
		kernel32 = ctypes.windll.kernel32
		HANDLE = ctypes.c_void_p
		DWORD = ctypes.c_ulong
		LPDWORD = ctypes.POINTER(DWORD)
		
		class ExitCodeProcess(ctypes.Structure):
			_fields_ = [("hProcess", HANDLE), ("lpExitCode", LPDWORD)]

		SYNCHRONIZE = 0x100000
		process = kernel32.OpenProcess(SYNCHRONIZE, 0, pid)
		if not process:
			return False

		ec = ExitCodeProcess()
		out = kernel32.GetExitCodeProcess(process, ctypes.byref(ec))
		if not out:
			if kernel32.GetLastError() == 5:
				# Access is denied.
				print("Access is denied when getting PID info")
			kernel32.CloseHandle(process)
			return False
		elif bool(ec.lpExitCode):
			# There is an exit code, it quit
			kernel32.CloseHandle(process)
			return False
		# No exit code, it"s running.
		kernel32.CloseHandle(process)
		return True


# Run test for `.stop()` only as the last test in CI environments – it would be to annoying
# during normal testing
@pytest.mark.last
def test_daemon_stop(client):
	have_ci  = os.environ.get("CI", "false") == "true"
	have_pid = os.environ.get("PY_IPFS_HTTP_CLIENT_TEST_DAEMON_PID", "").isdigit()
	if not have_ci or not have_pid:
		pytest.skip("CI-only test")
	daemon_pid = int(os.environ["PY_IPFS_HTTP_CLIENT_TEST_DAEMON_PID"])
	
	# Daemon should still be running at this point
	assert check_pid_exists(daemon_pid)
	
	# Send stop request
	client.stop()
	
	# Wait for daemon process to disappear
	for _ in range(10000):
		if not check_pid_exists(daemon_pid):
			break
		time.sleep(0.001)
	
	# Daemon should not be running anymore
	assert not check_pid_exists(daemon_pid)