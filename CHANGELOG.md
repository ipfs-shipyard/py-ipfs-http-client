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
