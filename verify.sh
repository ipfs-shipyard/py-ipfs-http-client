#!/usr/bin/env bash

set -e

function validate() {
	./tools/verify/validate.sh "$1"
}

if [ -z "$1" ]; then
    echo "Validating minimum point release of each supported minor version..."

    # Maintain this concurrently with [tool.flit.metadata].requires-python in pyproject.toml.
    validate 3.7.2
    validate 3.8.0
    validate 3.9.0
else
    echo "Validating only $1..."
    validate "$1"
fi
