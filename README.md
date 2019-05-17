# py-ipfs-http-client

[![Made by the IPFS Community](https://img.shields.io/badge/made%20by-IPFS%20Community-blue.svg?style=flat-square)](https://docs.ipfs.io/community/)
[![](https://img.shields.io/badge/project-IPFS-blue.svg?style=flat-square)](https://ipfs.io/)
[![IRC #py-ipfs on chat.freenode.net](https://img.shields.io/badge/freenode%20IRC-%23py--ipfs-blue.svg?style=flat-square)](http://webchat.freenode.net/?channels=%23py-ipfs)
[![Matrix #py-ipfs:ninetailed.ninja](https://img.shields.io/matrix/py-ipfs:ninetailed.ninja?color=blue&label=matrix+chat&style=flat-square)](https://matrix.to/#/#py-ipfs:ninetailed.ninja?via=ninetailed.ninja&via=librem.one)
[![Standard README Compliant](https://img.shields.io/badge/standard--readme-OK-green.svg?style=flat-square)](https://github.com/RichardLitt/standard-readme)
[![](https://img.shields.io/pypi/v/ipfshttpclient.svg?style=flat-square)](https://pypi.python.org/pypi/ipfshttpclient)
[![Build Status](https://travis-ci.org/ipfs/py-ipfs-http-client.svg?branch=master)](https://travis-ci.org/ipfs/py-ipfs-http-client)

![Python IPFS HTTP Client Library](https://ipfs.io/ipfs/QmQJ68PFMDdAsgCZvA1UVzzn18asVcf7HVvCDgpjiSCAse)

Check out [the HTTP Client reference](https://ipfs.io/ipns/12D3KooWEqnTdgqHnkkwarSrJjeMP2ZJiADWLYADaNvUb6SQNyPF/docs/) for the full command reference.

**Important:** The `ipfsapi` PIP package and Python module have both been renamed to `ipfshttpclient`!
See the [relevant section of the README](#important-changes-from-ipfsapi-04x) for details.

**Note:** This library constantly has to change to stay compatible with the IPFS HTTP API.
Currently, this library is tested against [go-ipfs v0.4.22](https://github.com/ipfs/go-ipfs/releases/tag/v0.4.22).
We strive to support the last 5 releases of go-IPFS at any given time; go-IPFS v0.4.18 therefor
being to oldest supported version at this time.

The following versions have been expliciently backlisted for know compatiblity problems:

  * 0.4.20

## Table of Contents

- [Install](#install)
- [Usage](#usage)
- [Documentation](#documentation)
  - [Important changes from ipfsapi 0.4.x](#important-changes-from-ipfsapi-04x)
- [Featured Projects](#featured-projects)
- [Contribute](#contribute)
  - [IRC](#irc)
  - [Bug reports](#bug-reports)
  - [Pull requests](#pull-requests)
- [License](#license)

## Install

Install with pip:

```sh
pip install ipfshttpclient
```

## Development install from Source

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
>>> client = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001/http')
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
>>> api = ipfshttpclient.connect('/dns/ipfs-api.example.com/tcp/443/https', username="foo", password="bar")
```

Pass custom headers to your IPFS api with each request:
```py
>>> import ipfshttpclient
>>> headers = {"CustomHeader": "foobar"}
>>> api = ipfshttpclient.connect('/dns/ipfs-api.example.com/tcp/443/https', headers=headers)
```



## Documentation

Documentation (currently mostly API documentation unfortunately) is available on IPFS:

https://ipfs.io/ipns/12D3KooWEqnTdgqHnkkwarSrJjeMP2ZJiADWLYADaNvUb6SQNyPF/docs/

The `ipfs` [command-line Client documentation](https://ipfs.io/docs/commands/) may also be useful in some cases.

### Important changes from `ipfsapi 0.4.x`

 * Tons of methods has been renamed, ensure that you code runs without warnings with the last version of `ipfsapi` before attempting to upgrade!
 * The Python package has been renamed from `ipfsapi` to `ipfshttpclient`
 * The PIP module has been renamed from `ipfsapi` to `ipfshttpclient` (please update your requirement files)
 * The `client.*_pyobj` family of functions has been dropped due to security concerns
 * The `client.bitswap.unwant` method has been dropped – it's endpoint has been removed by *go-ipfs*
 * The `client.files.file_ls` method has been dropped – deprecated for a long time, use `client.ls` instead
 * Passing a list of parameters to `client.add` will now fail, just pass several individual parameters instead
 * Some functions that may also return multiple items, will now also return a list when returning only a single item (don't worry about it unless it actually breaks for you)
 * The API deamon location is now described using Multiaddr, hence rather then doing `ipfshttpclient.connect(host, port)` to pass the network address parameters, use:
    * `ipfshttpclient.connect("/dns/<host>/tcp/<port>/http")` (for hostnames such as `localhost`)
    * `ipfshttpclient.connect("/ip4/<IP-address>/tcp/<port>/http")` (for IPv4 addresses)
    * `ipfshttpclient.connect("/ip6/<IP-address>/tcp/<port>/http")` (for IPv6 addresses)
    * Use `…/https` rather then `…/http` to connect to the API deamon using HTTPS
 * The client now supports [keeping session contexts around between API calls](#usage), you probably should make use of this facility in your code

Thank you @AlibabasMerchant, @lordcirth and @radfish (in order of subjective contributions) for helping making this happen!

## Featured Projects

Projects that currently use py-ipfs-http-client. If your project isn't here, feel free to submit a PR to add it!

- [git-remote-ipfs](https://github.com/larsks/git-remote-ipfs) allows users to push and pull git repositories from the IPFS network.
- [InterPlanetary Wayback](https://github.com/oduwsdl/ipwb) interfaces web archive ([WARC](https://www.iso.org/standard/44717.html)) files for distributed indexing and replay using IPFS.

## Contribute

### Chat (IRC/Matrix)

You can find us on [#py-ipfs on chat.freenode.org](http://webchat.freenode.net/?channels=%23py-ipfs) or in our [Matrix chat room](https://matrix.to/#/#py-ipfs:ninetailed.ninja?via=ninetailed.ninja&via=librem.one). Oin us if you have any suggestions, questions or if you just want to discuss IPFS and Python in general.

Please note that the channel is not monitored all the time and hence you may only receive a reply to your message later that day. Using Matrix makes it easier to stay connected in the background, so please prefer the Matrix option or use an IRC bouncer.

### Bug reports

You can submit bug reports using the [GitHub issue tracker](https://github.com/ipfs/py-ipfs-http-client/issues).

### Pull requests

Pull requests are welcome.  Before submitting a new pull request, please
make sure that your code passes both the [code formatting](https://www.python.org/dev/peps/pep-0008/) check:

    $ tox -e codestyle

And the unit tests:

    $ tox

You can arrange to run the code style tests automatically before each commit by
installing a `pre-commit` hook:

    $ ./tools/pre-commit --install

Please make sure to include new unit tests for new features or changes in
behavior. We aim to bring coverage to 100% at some point.

## License

This code is distributed under the terms of the [MIT license](https://opensource.org/licenses/MIT).  Details can be found in the file
[LICENSE](LICENSE) in this repository.
