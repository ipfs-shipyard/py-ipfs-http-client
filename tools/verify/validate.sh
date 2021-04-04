#!/bin/bash

set -e

python_version=$1
script_path=$(dirname $0)
source=$(realpath "$script_path/../..")
tag=py-ipfs-http-client-verify:$python_version

pushd "$script_path"

echo "Building validator for Python $python_version..."

docker build --build-arg PYTHON_VERSION="$python_version" -t "$tag" .

echo "Validating version $python_version"

docker run \
		-it \
		-v "$source/docs":/source/docs:ro \
		-v "$source/ipfshttpclient":/source/ipfshttpclient:ro \
		-v "$source/test":/source/test:ro \
		-v "$source/pyproject.toml":/source/pyproject.toml:ro \
		-v "$source/README.md":/source/README.md:ro \
		-v "$source/tox.ini":/source/tox.ini:ro \
		-w /usr/src/app \
		"$tag" \
		tox -e styleck -e typeck

popd

