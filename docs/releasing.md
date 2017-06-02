Since releasing new versions is currently a somewhat complicated task, the current procedure
(02.06.2017) will be outlined in this document.

All of this has only ever been tested on Debian 9 (Linux).

# Prerequirements

## Building and updating the project

### Python 3 with `setuptools` and `wheel` support

APT line: `sudo apt install python3-setuptools python3-wheel`

### PanDoc

PanDoc is used to on-the-fly convert the `README.md` to reStructuredText when running `./setup.py`.
This way we can keep all the project documentation in one (nice) format.

APT line: `sudo apt install pandoc`

## Building the documentation

### Sphinx & the `recommonmark` preprocessor

Sphinx is the standard documentation framework for Python. Recommonmark is an extension that allows
Sphinx to process Markdown documentation as if it where reStructuredText.

APT line: `sudo apt install python3-sphinx python3-recommonmark`

## Hosting Documentation

**Both of the following need to be on the device that will *host the documentation*, not the one
that will build it**:

### The Go IPFS daemon

Yes, we use IPFS to host our documentation. In case you haven't already you can download it here:
https://ipfs.io/docs/install/

### `ipfs-file-publish`

This small utility copies files or directories into the IPFS [MFS](https://ipfs.io/docs/commands/#ipfs-files)
and then publishes the resulting hash as the node's primary hash. This is currently used to upload
new versions of the documentation.

You can download it at:
https://ipfs.io/ipns/QmZ86ow1byeyhNRJEatWxGPJKcnQKG7s51MtbHdxxUddTH/Software/Python/ipfs-file-publish


# Steps when releasing a new version

## Update the source code

 1. Make a GIT commit incrementing the version number in `ipfsapi/version.py` (`git commit ipfsapi/version.py`)
 2. Tag the GIT commit with the version number (`git tag 0.4.X`)
 3. Push the new version

## Upload the new version to PyPI

Run: `./setup.py sdist bdist_wheel upload`

**You must have `pandoc` installed or the description PyPI will be replaced with nothing!**

## Re-generate the documentation

Run: `make -C docs/ html`

## Publish the documentation

Make sure an IPFS daemon is running and run: `ipfs-file-publish /Software/Python/ipfsapi/ docs/build/html/`
