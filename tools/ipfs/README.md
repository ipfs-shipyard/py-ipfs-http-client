
# Running Tests

Tests are primarily run from the command line using a locally installed IPFS server.

Alternatively, you can launch the IPFS daemon with Docker and run tests from your IDE.


## Local IPFS Server Installation

To install it, follow the [official instructions](https://docs.ipfs.io/install/command-line/).

Remaining configuration is applied by [run_tests.py](../../test/run-tests.py) on each run.


## Running Tests Using Local Installation From Command Line

* `tox -e py3`
* `tox -e py3-httpx`


## Running Tests Using Docker from IDE (e.g. PyCharm)

1. Start [daemon.sh](daemon.sh)
2. Run `pytest` tests from your IDE as your normally would

You can keep the Docker container running across multiple
executions of the functional test suite.


## Running Tests Without Live Server

You can run unit tests without a live server; `pytest` will skip
over the functional tests when our fixtures detect the server
isn't running.


## pytest-docker Plugin

While `pytest-docker` supports running functional tests against a
Docker container using Docker Compose, it is not supported on
Windows or Mac with Travis and IPFS.

