# py-ipfs-api

[![](https://img.shields.io/badge/made%20by-Protocol%20Labs-blue.svg?style=flat-square)](http://ipn.io)
[![](https://img.shields.io/badge/project-IPFS-blue.svg?style=flat-square)](http://ipfs.io/)
[![](https://img.shields.io/badge/freenode-%23ipfs-blue.svg?style=flat-square)](http://webchat.freenode.net/?channels=%23ipfs)
[![standard-readme compliant](https://img.shields.io/badge/standard--readme-OK-green.svg?style=flat-square)](https://github.com/RichardLitt/standard-readme)
[![](https://img.shields.io/pypi/v/ipfsapi.svg?style=flat-square)](https://pypi.python.org/pypi/ipfsapi)
[![](https://img.shields.io/travis/ipfs/py-ipfs-api.svg?style=flat-square)](https://travis-ci.org/ipfs/py-ipfs-api)

> A python client library for the IPFS API

Check out [the client API reference](https://ipfs.io/ipns/QmZ86ow1byeyhNRJEatWxGPJKcnQKG7s51MtbHdxxUddTH/Software/Python/ipfsapi/) for the full command reference.

**Note:** This library constantly has to change to stay compatible with the IPFS HTTP API.
Currently, this library is tested against [go-ipfs v0.4.3](https://github.com/ipfs/go-ipfs/releases/tag/v0.4.3).
You may experience compatibility issues when attempting to use it with other versions of go-ipfs.

## Table of Contents

- [Install](#install)
- [Usage](#usage)
- [Documentation](#documentation)
  - [Important changes from ipfsApi 0.2.x](#important-changes-from-ipfsapi-02x)
- [Featured Projects](#featured-projects)
- [Contribute](#contribute)
  - [IRC](#irc)
  - [Bug reports](#bug-reports)
  - [Pull requests](#pull-requests)
- [License](#license)

## Install

Install with pip:

```sh
pip install ipfsapi
```

## Usage

Basic use-case (requires a running instance of IPFS daemon):

```py
>>> import ipfsapi
>>> api = ipfsapi.connect('127.0.0.1', 5001)
>>> res = api.add('test.txt')
>>> res
{'Hash': 'QmWxS5aNTFEc9XbMX1ASvLET1zrqEaTssqt33rVZQCQb22', 'Name': 'test.txt'}
>>> api.cat(res['Hash'])
'fdsafkljdskafjaksdjf\n'
```

Administrative functions:

```py
>>> api.id()
{'Addresses': ['/ip4/127.0.0.1/tcp/4001/ipfs/QmS2C4MjZsv2iP1UDMMLCYqJ4WeJw8n3vXx1VKxW1UbqHS',
               '/ip6/::1/tcp/4001/ipfs/QmS2C4MjZsv2iP1UDMMLCYqJ4WeJw8n3vXx1VKxW1UbqHS'],
 'AgentVersion': 'go-ipfs/0.3.8-dev',
 'ID': 'QmS2C4MjZsv2iP1UDMMLCYqJ4WeJw8n3vXx1VKxW1UbqHS',
 'ProtocolVersion': 'ipfs/0.1.0',
 'PublicKey': 'CAASpgIwgg ... 3FcjAgMBAAE='}
```

Pass in API options:

```py
>>> api.pin_ls(type='all')
{'Keys': {'QmNMELyizsfFdNZW3yKTi1SE2pErifwDTXx6vvQBfwcJbU': {'Count': 1,
                                                             'Type': 'indirect'},
          'QmNQ1h6o1xJARvYzwmySPsuv9L5XfzS4WTvJSTAWwYRSd8': {'Count': 1,
                                                             'Type': 'indirect'},
          …
```

Add a directory and match against a filename pattern:

```py
>>> api.add('photos', match='*.jpg')
[{'Hash': 'QmcqBstfu5AWpXUqbucwimmWdJbu89qqYmE3WXVktvaXhX',
  'Name': 'photos/photo1.jpg'},
 {'Hash': 'QmSbmgg7kYwkSNzGLvWELnw1KthvTAMszN5TNg3XQ799Fu',
  'Name': 'photos/photo2.jpg'},
 {'Hash': 'Qma6K85PJ8dN3qWjxgsDNaMjWjTNy8ygUWXH2kfoq9bVxH',
  'Name': 'photos/photo3.jpg'}]
```

Or add a directory recursively:

```py
>>> api.add('fake_dir', recursive=True)
[{'Hash': 'QmQcCtMgLVwvMQGu6mvsRYLjwqrZJcYtH4mboM9urWW9vX',
  'Name': 'fake_dir/fsdfgh'},
 {'Hash': 'QmNuvmuFeeWWpxjCQwLkHshr8iqhGLWXFzSGzafBeawTTZ',
  'Name': 'fake_dir/test2/llllg'},
 {'Hash': 'QmX1dd5DtkgoiYRKaPQPTCtXArUu4jEZ62rJBUcd5WhxAZ',
  'Name': 'fake_dir/test2'},
 {'Hash': 'Qmenzb5J4fR9c69BbpbBhPTSp2Snjthu2hKPWGPPJUHb9M',
  'Name': 'fake_dir'}]
```

This module also contains some helper functions for adding strings, json, and even python objects to IPFS:

```py
>>> lst = [1, 77, 'lol']
>>> api.add_pyobj(lst)
'QmRFqz1ABQtbMBDfjpMubTaginvpVnf58Y87gheRzGfe4i'
>>> api.get_pyobj(_)
[1, 77, 'lol']
```

## Documentation

Documentation (currently mostly API documentation unfortunately) is available on IPFS:

https://ipfs.io/ipns/QmZ86ow1byeyhNRJEatWxGPJKcnQKG7s51MtbHdxxUddTH/Software/Python/ipfsapi/

The `ipfs` [command-line Client documentation](https://ipfs.io/docs/commands/) may also be useful in some cases.

### Important changes from `ipfsApi 0.2.x`

 * The Python package has been renamed from `ipfsApi` to `ipfsapi`
 * The PIP module has been renamed from `ipfs-api` to `ipfsapi` (please update your requirement files)
 * A lot of changes in the internal code
    - Commands have been completely removed
    - Usage of `requests` or other libraries is considered an implementation detail from now on
 * Most parts of the library (except for `Client()`) are now considered internal and may therefore break at any time
   ([reference](https://ipfs.io/ipns/QmZ86ow1byeyhNRJEatWxGPJKcnQKG7s51MtbHdxxUddTH/Software/Python/ipfsapi/internal_ref.html))
    - We will try to keep breakage for these modules at a minimum
    - If you require stabilisation of some feature please open an issue with the feature in question and your preceived use-case
 * Raised exceptions have been completely changed and are now documented with guaranteed backwards compatibility
   ([reference](https://ipfs.io/ipns/QmZ86ow1byeyhNRJEatWxGPJKcnQKG7s51MtbHdxxUddTH/Software/Python/ipfsapi/api_ref.html#module-ipfsapi.exceptions))
 * Methods in `Client()` now have parameters for options

## Featured Projects

Projects that currently use py-ipfs-api. If your project isn't here, feel free to submit a PR to add it!

- [git-remote-ipfs](https://github.com/larsks/git-remote-ipfs) allows users to push and pull git repositories from the IPFS network.

## Contribute

### IRC

Join us on IRC at `#ipfs` on [chat.freenode.net](https://webchat.freenode.net) if you have any suggestions or questions,
or if you just want to discuss IPFS and python.

### Bug reports

You can submit bug reports using the [GitHub issue tracker](https://github.com/ipfs/python-ipfs-api/issues).

### Pull requests

Pull requests are welcome.  Before submitting a new pull request, please
make sure that your code passes both the [pep8](https://www.python.org/dev/peps/pep-0008/) formatting check:

    $ tox -e pep8

And the unit tests:

    $ tox

You can arrange to run the pep8 tests automatically before each commit by
installing a `pre-commit` hook:

    $ ./tools/pre-commit --install

Please make sure to include new unit tests for new features or changes in
behavior.

## License

This code is distributed under the terms of the [MIT license](https://opensource.org/licenses/MIT).  Details can be found in the file
[LICENSE](LICENSE) in this repository.
