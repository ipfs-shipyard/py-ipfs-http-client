#!/bin/sh
export IPFS_PATH="$(pwd)/test-tmp"
export PY_IPFSAPI_DEFAULT_HOST="127.0.0.1"
export PY_IPFSAPI_DEFAULT_PORT="$(shuf -i 40000-65535 -n 1)"

# Delete any left-over IPFS directory
rm -rf "${IPFS_PATH}"

# Create new IPFS instance directory
ipfs init
ipfs config Addresses.Gateway ""
ipfs config Addresses.API     "/ip4/${PY_IPFSAPI_DEFAULT_HOST}/tcp/${PY_IPFSAPI_DEFAULT_PORT}"

# Start IPFS daemon in instance directory
ipfs daemon &
export PY_IPFSAPI_TEST_DAEMON_PID=$!

# Wait for daemon startup
while ! curl "http://${PY_IPFSAPI_DEFAULT_HOST}:${PY_IPFSAPI_DEFAULT_PORT}/api/v0/stats/bw" >/dev/null 2>&1;
do
	sleep 0.1
done

# Run tests in CI-mode (will stop the daemon at the end through the API)
export CI=true
if [ "${1}" = "tox" ];
then
	tox
else
	py.test-3 --verbose --pdb
fi
CODE=$?

# Stop daemon if it is still running
kill -9 ${PY_IPFSAPI_TEST_DAEMON_PID} 2>/dev/null
if [ $? -eq 0 ];
then
	echo "IPFS daemon was still running after test!" >&2
fi

# Clean up IPFS directory
rm -rf "${IPFS_PATH}"

exit ${CODE}
