py-ipfs-http-client 0.X.X (XX.XX.20XX)
--------------------------------------

 * (None yet)

py-ipfs-http-client 0.7.0 (15.03.2021)
--------------------------------------

 * No changes compared to 0.7.0a1 – breaking changes delayed to the unknown future


py-ipfs-http-client 0.7.0a1 (14.10.2020)
--------------------------------------

 * Added support for optional arguments of the `.dag.*` APIs (by João Meyer)
 * Compatiblity bumped to go-IPFS 0.7.x (by Jan Rydzewski and other community members bugging me)
 * The 0.7 series is not stable yet, expect some breaking changes before the final release!


py-ipfs-http-client 0.6.1 (26.08.2020)
--------------------------------------

 * Added typings for most of the public and private API and enable type checking with `mypy`
 * Added support for connecting to the IPFS daemon using Unix domain sockets (implemented for both the requests and HTTPx backend)
 * Deprecate `.repo.gc(…)`s `return_result` parameter in favour of the newly introduced `quiet` parameter to match the newer HTTP API
 * If you use the undocumented `return_result` parameter anywhere else consider such use deprecated, support for this parameter will be removed in 0.7.X everywhere
    * Rationale: This parameter used to map to using the HTTP HEAD method perform the given request without any reply being returned, but this feature has been dropped with go-IPFS 0.5 from the API.
 * Implemented DAG APIs for go-IPFS 0.5+: `.dag.get`, `.dag.put`, `.dag.imprt` and `.dag.export`

Bugfixes:

 * The value of the `timeout` parameter on `ipfshttpclient.{connect,Client}` is no longer ignored when using the `requests` HTTP backend (default)
    * (The per-API-call `timeout` parameter was unaffected by this.)
 * The HTTPx HTTP backend now properly applies address family restrictions encoded as part of the daemon MultiAddr (needed minor upstream change)

py-ipfs-http-client 0.6.0 (30.06.2020)
--------------------------------------

**Breaking changes in this release**:

 * The *recursive* parameter of `.add()` is no longer ignored and now enforces its default value of `False` (explicitely set it to `True` for the previous behaviour)
 * The glob pattern strings that may be passed to the `.add()` pattern parameter now actually behave like recursive glob patterns (see [the Python documentation](https://docs.python.org/3/library/glob.html) for how exactly)
 * Most functions previously returning a dict with the raw JSON response, now return a custom mapping type instead
    * This mapping type supports the original getitem syntax (`result["ItemName"]`) unchanged, but if you need an actual dictionary object you need to call `.as_json()` on it
    * In the future response-specific subtypes with Pythonic accessors and object specific methods will hopefully be added
 * HTTP basic authentication data to send to the API daemon must now be set as an `auth=(username, password)` tuple rather than using separate `username=` and `password=` parameters

Other changes:

 * Added support for go-IPFS 0.5.x
 * Adding directories with `.add()` has been greatly reworked:
    * Its now possible to specify arbitrary rules on which objects to include a directory tree by passing a custom matcher object to the *pattern* parameter
    * The new *period_special* parameter allows toggling whether glob patterns match dot-files implicietly and defaults to `True` (previously it was effectively `False`)
    * The new *follow_symlinks* parameter similarily determines whether symbolic links will be followed when scanning directory trees and defaults to `False` (the previous default on Unix, albeit this likely wasn't intentional)
    * `.add()` will now limit its scan to the directories required to match the given glob patterns (passing in regular expression objects will still scan the tree unconditionally however) – custom matchers have full control over which directories are visited
 * The requests-based HTTP backend has been supplemented by another backend based on [HTTPx](https://www.python-httpx.org/) for Python 3.6+
    * Due to a minor limitation within the library (no ability to apply address family restrictions during name resolution) this currently included as a preview and must be manually enabled, to do this ensure that the `httpx` library is installed in your Python environment and run your program with the environment variable *PY_IPFS_HTTP_CLIENT_PREFER_HTTPX* set to *yes*.
    * In the hopefully not too long future, HTTPx will be used to finally provide async/await support for this library.

py-ipfs-http-client 0.4.12 (21.05.2019)
---------------------------------------

Bug fix release:

 * Fix compatibility with `urllib3` 1.25.* when connecting to HTTPS API servers

py-ipfs-http-client 0.4.11 (13.05.2019)
---------------------------------------

(Most of the following was also released as version 0.4.10 the previous day, but that release was never advertised and some issues were quickly found that necessitated a new release.)

This release features several breaking changes, as compared to the previous *py-ipfs-api* library

 * A new import name: `ipfsapi` → `ipfshttpclient` (thanks to @AlibabasMerchant)
 * The client API is now structured according to the [IPFS interface core specification](https://github.com/ipfs/interface-ipfs-core/tree/master/SPEC)
 * Deamon location is now described using [Multiaddr](https://github.com/multiformats/multiaddr)
 * Some deprecated methods have been dropped:
    * `bitswap_unwant`: API endpoint dropped by *go-ipfs*
    * `{get,set}_pyobj`: Can too easily be abused for abitrary code execution, use `pickle.{loads,dumps}` if you really need this
    * `file_ls`: Long deprecated by *go-ipfs* and scheduled for removal, use plain `ls` instead

Some new features added in this release:

 * Adding large directories doesn't read them all into memory anymore before sending them to the daemon
 * API documentation has been improved
 * TCP connections may now be reused between API requests
 * `.add_json` now adds data as UTF-8 rather than using Unicode-escapes for shorter/more-canoncial data representation (thanks to @emmnx)
 * Several parameters have been added to existing methods:
    * Using [filestore](https://github.com/ipfs-filestore/go-ipfs/tree/master/filestore) is now possible (thanks to @radfish)
    * Universal per-call `offline` parameter added (thanks to @radfish)
    * Universal per-call `return_result` parameter added to issue `HEAD` requests and surpress results for speeds (thanks to @loardcirth)
    * Universal per-call `timeout` parameter added (thanks to @AlibabasMerchant)
    * `.add`: `nocopy` & `raw_leaves` (thanks to @radfish)
    * `.ls`: `paths` (thanks to @radfish)
    * `.name.publish`: `allow_offline` (thanks to @radfish)
    * `.name.resolve`: `dht_record_count` & `dht_timeout` (thanks to @radfish)

*go-ipfs* 0.4.20 has been blacklisted for having know compatibility problems, but 0.4.19 and 0.4.21 are OK.

py-ipfs-api 0.4.4 (13.05.2019)
------------------------------

 * Reimplement library as thin wrapper around the new *py-ipfs-http-client* library with helpful warnings about how to upgrade
