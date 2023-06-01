#!/bin/sh

set -e

# Only does configuration; doesn't start the daemon
/usr/local/bin/start_ipfs

echo "Enabling experimental features"

ipfs config --json Experimental.FilestoreEnabled true

echo "Enabled experimental features"

# Start the daemon (unless other args provided)
exec "$@"
