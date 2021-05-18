
# Release

The release process uses `flit` to build the package, `Sphinx` to generate documentation, 
publishes the documentation to an IPFS server (obtaining an IPFS hash), and then links
the IPFS hash (which varies based on content) to a static IPNS name.

The IPNS name requires a private key, which is controlled by the project owners and not
available to the public.

All steps can be completed up through but not including linking the IPFS hash to IPNS.


## Pre-Requisites

* On Debian
* Python 3.8+ (or typings will be incomplete)


## One-Time Setup

Install the release tools into your virtual environment:

    $ pip install -r tools/release/requirements.txt

Source: [tools/release/requirements.txt](tools/release/requirements.txt)


### The Go IPFS daemon

Yes, we use IPFS to host our documentation. In case you haven't already you can download it here:
https://ipfs.io/docs/install/


### A dedicated IPNS key for publishing

For publishing the documentation an IPNS key used only for this task should be
generated if there is no such key already:

`ipfs key gen --type ed25519 ipfs-http-client`

This key will need to be copied to all other servers hosting the IPNS link.
Without the private key, other servers can host the IPFS files, but not the IPNS link.

At the time of writing the officially used key is: *12D3KooWEqnTdgqHnkkwarSrJjeMP2ZJiADWLYADaNvUb6SQNyPF*


# Steps

## Update the source code

 1. Make a GIT commit
    * Incrementing the version number in `ipfshttpclient/version.py`
    * Completing the currently open `CHANGELOG.md` entry

    `git commit -m "Release version 0.X.Y" ipfshttpclient/version.py CHANGELOG.md`

 2. After the change is merged into master, pull master 

 3. Tag the GIT commit with the version number using an annotated and signed tag:

    `git tag --sign -m "Release version 0.X.Y" 0.X.Y`

 4. Push the new tag


## Upload the new version to PyPI

Run:

    $ flit build && flit publish

## Re-generate and publish the documentation

Run:

    $ python docs/publish.py ipns-key-id

The command will also print a commandline that may be used to mirror the generated
documentation on systems other then the current one.

If you don't have the IPNS private key, you can still exercise the documentation 
generation and publish process:

    $ python docs/publish.py

If you are publishing to an IPFS server that is remote, and protected by an HTTP reverse proxy
with TLS and basic authentication, run this instead:

    $ IPFS_API_MULTI_ADDR=/dns/yourserver.tld/tcp/5001/https IPFS_API_USERNAME=basicauthuser IPFS_API_PASSWORD=basicauthpassword python publish.py ipns-key-id

