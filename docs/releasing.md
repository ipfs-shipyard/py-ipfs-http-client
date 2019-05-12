Since releasing new versions is currently a somewhat complicated task, the current procedure
(12.05.2018) will be outlined in this document.

All of this has only been tested on Debian 10 & Fedora 28 (Linux).

# Prerequirements

## Building and updating the project

### Python 3 with the `flit` project manager

APT line: `sudo apt install python3-pip && sudo pip3 install flit`  
DNF line: `sudo dnf install python3-flit`

*Note*: Version `1.1+` of `flit` is required!

## Building the documentation

### Sphinx & the `recommonmark` preprocessor

Sphinx is the standard documentation framework for Python. Recommonmark is an extension that allows
Sphinx to process Markdown documentation as if it where reStructuredText.

<!-- APT line: `sudo apt install python3-sphinx python3-recommonmark`  -->
<!--DNF line: `sudo dnf install python3-sphinx python3-recommonmark`-->

At least reCommonMark 0.5 is required, so install it using PIP:

`pip3 install recommonmark~=0.5.0`

## Hosting Documentation

**Both of the following need to be on the device that will *host the documentation*, not the one
that will build it**:

### The Go IPFS daemon

Yes, we use IPFS to host our documentation. In case you haven't already you can download it here:
https://ipfs.io/docs/install/

### A dedicated IPNS key for publishing

For publishing the documentation an IPNS key used only for this task should be
generated if there is no such key already:

`ipfs key gen --type ed25519 ipfs-http-client`

This key will need to be copied to all other system if the documentation is to
be published on these as well.

At the time of writing the officially used key is: *12D3KooWEqnTdgqHnkkwarSrJjeMP2ZJiADWLYADaNvUb6SQNyPF*


# Steps when releasing a new version

## Update the source code

 1. Make a GIT commit incrementing the version number in `ipfshttpclient/version.py`:  
    `git commit -m "Release version 0.4.X" ipfshttpclient/version.py`)
 2. Tag the GIT commit with the version number using an annotated and signed tag:  
    `git tag --sign -m "Release version 0.4.X" 0.4.X`
 3. Push the new version

## Upload the new version to PyPI

Run: `flit build && flit upload`

## Re-generate and publish the documentation

Run: `docs/publish.py ipfs-http-client` (were `ipfs-http-client` is the IPNS key ID)

The command will also print a commandline that may be used to mirror the generated
documentation on systems other then the current one.
