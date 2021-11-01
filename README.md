# py-ipfs-http-client

[![Made by the IPFS Community](https://img.shields.io/badge/made%20by-IPFS%20Community-blue.svg?style=flat-square)](https://docs.ipfs.io/community/)
[![IRC #py-ipfs on chat.freenode.net](https://img.shields.io/badge/freenode%20IRC-%23py--ipfs-blue.svg?style=flat-square)](http://webchat.freenode.net/?channels=%23py-ipfs)
[![Matrix #py-ipfs:ninetailed.ninja](https://img.shields.io/matrix/py-ipfs:ninetailed.ninja?color=blue&label=matrix%20chat&server_fqdn=matrix.ninetailed.ninja&style=flat-square)](https://matrix.to/#/#py-ipfs:ninetailed.ninja?via=matrix.ninetailed.ninja&via=librem.one)
[![Standard README Compliant](https://img.shields.io/badge/standard--readme-OK-green.svg?style=flat-square)](https://github.com/RichardLitt/standard-readme)
[![PyPI Package ipfshttpclient](https://img.shields.io/pypi/dm/ipfshttpclient.svg?style=flat-square)](https://pypi.python.org/pypi/ipfshttpclient)
[![Build Status](https://img.shields.io/travis/com/ipfs-shipyard/py-ipfs-http-client/master.svg?style=flat-square)](https://travis-ci.com/github/ipfs-shipyard/py-ipfs-http-client)

![Python IPFS HTTP Client Library](https://ipfs.io/ipfs/QmQJ68PFMDdAsgCZvA1UVzzn18asVcf7HVvCDgpjiSCAse)

# A fork of [ipfs-shipyard/py-ipfs-http-client](https://github.com/ipfs-shipyard/py-ipfs-http-client), the official ipfshttpclient python module, which I have expanded to access IPFS's LibP2PStreamMounting feature.

Check out [the HTTP Client reference](https://ipfs.io/ipns/12D3KooWEqnTdgqHnkkwarSrJjeMP2ZJiADWLYADaNvUb6SQNyPF/docs/) for the full command reference.

**Note**: The `ipfsapi` PIP package and Python module have both been renamed to `ipfshttpclient`!
See the [relevant section of the CHANGELOG](CHANGELOG.md#py-ipfs-http-client-0411-13052019) for details. There is also a `ipfsApi` library from which this library originated that is completely
unmaintained and does not work with any recent go-IPFS version.

**Note**: This library occasionally has to change to stay compatible with the IPFS HTTP API.
Currently, this library is tested against [go-ipfs v0.8.0](https://github.com/ipfs/go-ipfs/releases/tag/v0.8.0).
We strive to support the last 5 releases of go-IPFS at any given time; go-IPFS v0.5.0 therefore
being to oldest supported version at this time.

## Table of Contents

- [Install](#install)
- [Usage](#usage)
- [Documentation](#documentation)
  - [Migrating from 0.4.x to 0.6.0](#migrating-from-04x-to-060)
- [Featured Projects](#featured-projects)
- [Contributing](#contributing)
  - [Easy Tasks](#easy-tasks)
  - [Bug reports](#bug-reports)
  - [Setting up a local development environment](#setting-up-a-local-development-environment)
  - [Pull requests](#pull-requests)
  - [Chat with Us (IRC/Matrix)](#chat-with-us-ircmatrix)
- [License](#license)

## Install

Install with pip:

```sh
pip install ipfshttpclient
```

### Development install from Source

```sh
# Clone the source repository
git clone https://github.com/ipfs/py-ipfs-http-client.git
cd py-ipfs-http-client

# Link ipfs-api-client into your Python Path
flit install --pth-file
```

## Usage

Basic use-case (requires a running instance of IPFS daemon):

```py
>>> import ipfshttpclient
>>> client = ipfshttpclient.connect()  # Connects to: /dns/localhost/tcp/5001/http
>>> res = client.add('test.txt')
>>> res
{'Hash': 'QmWxS5aNTFEc9XbMX1ASvLET1zrqEaTssqt33rVZQCQb22', 'Name': 'test.txt'}
>>> client.cat(res['Hash'])
'fdsafkljdskafjaksdjf\n'
```

*Please note*: You should specify the address for an IPFS *API server*, using the address of a *gateway* (such as the public `ipfs.io` one at `/dns/ipfs.io/tcp/443/https`) will only give you [extremely limited access](https://github.com/ipfs/go-ipfs/blob/master/docs/gateway.md#read-only-api) and may not work at all. If you are only interested in downloading IPFS content through public gateway servers then this library is unlikely of being of much help.

For real-world scripts you can reuse TCP connections using a context manager or manually closing the session after use:

```py
import ipfshttpclient

# Share TCP connections using a context manager
with ipfshttpclient.connect() as client:
	hash = client.add('test.txt')['Hash']
	print(client.stat(hash))

# Share TCP connections until the client session is closed
class SomeObject:
	def __init__(self):
		self._client = ipfshttpclient.connect(session=True)

	def do_something(self):
		hash = self._client.add('test.txt')['Hash']
		print(self._client.stat(hash))

	def close(self):  # Call this when your done
		self._client.close()
```

Administrative functions:

```py
>>> client.id()
{'Addresses': ['/ip4/127.0.0.1/tcp/4001/ipfs/QmS2C4MjZsv2iP1UDMMLCYqJ4WeJw8n3vXx1VKxW1UbqHS',
               '/ip6/::1/tcp/4001/ipfs/QmS2C4MjZsv2iP1UDMMLCYqJ4WeJw8n3vXx1VKxW1UbqHS'],
 'AgentVersion': 'go-ipfs/0.4.10',
 'ID': 'QmS2C4MjZsv2iP1UDMMLCYqJ4WeJw8n3vXx1VKxW1UbqHS',
 'ProtocolVersion': 'ipfs/0.1.0',
 'PublicKey': 'CAASpgIwgg ... 3FcjAgMBAAE='}
```

Pass in API options:

```py
>>> client.pin.ls(type='all')
{'Keys': {'QmNMELyizsfFdNZW3yKTi1SE2pErifwDTXx6vvQBfwcJbU': {'Count': 1,
                                                             'Type': 'indirect'},
          'QmNQ1h6o1xJARvYzwmySPsuv9L5XfzS4WTvJSTAWwYRSd8': {'Count': 1,
                                                             'Type': 'indirect'},
          …
```

Add a directory and match against a filename pattern:

```py
>>> client.add('photos', pattern='*.jpg')
[{'Hash': 'QmcqBstfu5AWpXUqbucwimmWdJbu89qqYmE3WXVktvaXhX',
  'Name': 'photos/photo1.jpg'},
 {'Hash': 'QmSbmgg7kYwkSNzGLvWELnw1KthvTAMszN5TNg3XQ799Fu',
  'Name': 'photos/photo2.jpg'},
 {'Hash': 'Qma6K85PJ8dN3qWjxgsDNaMjWjTNy8ygUWXH2kfoq9bVxH',
  'Name': 'photos/photo3.jpg'}]
```

Or add a directory recursively:

```py
>>> client.add('fake_dir', recursive=True)
[{'Hash': 'QmQcCtMgLVwvMQGu6mvsRYLjwqrZJcYtH4mboM9urWW9vX',
  'Name': 'fake_dir/fsdfgh'},
 {'Hash': 'QmNuvmuFeeWWpxjCQwLkHshr8iqhGLWXFzSGzafBeawTTZ',
  'Name': 'fake_dir/test2/llllg'},
 {'Hash': 'QmX1dd5DtkgoiYRKaPQPTCtXArUu4jEZ62rJBUcd5WhxAZ',
  'Name': 'fake_dir/test2'},
 {'Hash': 'Qmenzb5J4fR9c69BbpbBhPTSp2Snjthu2hKPWGPPJUHb9M',
  'Name': 'fake_dir'}]
```

This module also contains some helper functions for adding strings and JSON to IPFS:

```py
>>> lst = [1, 77, 'lol']
>>> client.add_json(lst)
'QmQ4R5cCUYBWiJpNL7mFe4LDrwD6qBr5Re17BoRAY9VNpd'
>>> client.get_json(_)
[1, 77, 'lol']
```

Use an IPFS server with basic auth (replace username and password with real creds):

```py
>>> import ipfshttpclient
>>> client = ipfshttpclient.connect('/dns/ipfs-api.example.com/tcp/443/https', auth=("username", "password"))
```

Pass custom headers to the IPFS daemon with each request:
```py
>>> import ipfshttpclient
>>> headers = {"CustomHeader": "foobar"}
>>> client = ipfshttpclient.connect('/dns/ipfs-api.example.com/tcp/443/https', headers=headers)
```

Connect to the IPFS daemon using a Unix domain socket (plain HTTP only):
```py
>>> import ipfshttpclient
>>> client = ipfshttpclient.connect("/unix/run/ipfs/ipfs.sock")
```



## Documentation

Documentation (currently mostly API documentation unfortunately) is available on IPFS:

https://ipfs.io/ipns/12D3KooWEqnTdgqHnkkwarSrJjeMP2ZJiADWLYADaNvUb6SQNyPF/docs/

The `ipfs` [command-line Client documentation](https://ipfs.io/docs/commands/) may also be useful in some cases.

### Migrating from `0.4.x` to `0.6.0`

Please see the CHANGELOG for [the minor breaking changes between these releases](CHANGELOG.md#py-ipfs-http-client-060-30062020).

## Featured Projects

Projects that currently use py-ipfs-http-client. If your project isn't here, feel free to submit a PR to add it!

- [InterPlanetary Wayback](https://github.com/oduwsdl/ipwb) interfaces web archive ([WARC](https://www.iso.org/standard/44717.html)) files for distributed indexing and replay using IPFS.

## Contributing

### Easy Tasks

Over time many smaller day-to-day tasks have piled up (mostly supporting some
newer APIs). If want to help out without getting too involved picking up one
of tasks of our [help wanted issue list](https://github.com/ipfs-shipyard/py-ipfs-http-client/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22)
would go a long way towards making this library more feature-complete. 👍

### Bug reports

You can submit bug reports using the
[GitHub issue tracker](https://github.com/ipfs/py-ipfs-http-client/issues).

### Setting up a local development environment

 1. Follow the instructions in the IPFS documentation to install go-IPFS into your `${PATH}`:  
    https://docs.ipfs.io/install/command-line/
 2. Follow the instructions in the (Python) tox documentation to install the `tox` Python environment runner:  
    https://tox.readthedocs.io/en/latest/install.html
 3. Clone the GIT repository if you haven't already:  
    `git clone https://github.com/ipfs-shipyard/py-ipfs-http-client.git`

If you want to you can also make your local development version of
*py-ipfs-http-client* available to your Python environment by
[installing `flit`](https://flit.readthedocs.io/en/latest/#install)
and running `flit install --pth-file` from the repository root.

Please see the next section for how to run tests and contribute code
back into the project.
