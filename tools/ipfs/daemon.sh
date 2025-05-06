#!/bin/bash

set -e

tag=py-ipfs-http-client-daemon:latest

docker build -t $tag .
docker run --rm -p 4001:4001 -p 5001:5001 -p 8080:8080 $tag

