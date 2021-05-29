#!/usr/bin/python3
import os
import sphinx.cmd.build
import sys
import typing as ty

script_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(script_dir, ".."))

import ipfshttpclient

os.chdir(script_dir)


def main(argv: ty.List[str]) -> int:
	if len(argv) >= 1:
		ipns_key = argv[0]
	else:
		ipns_key = None

		print("Usage: {0} [IPNS-key]".format(os.path.basename(__file__)))
		print()
		print('To connect to a remote IPFS daemon, set environment variables:')
		print()
		print('    PY_IPFS_HTTP_CLIENT_DEFAULT_ADDR')
		print('    PY_IPFS_HTTP_CLIENT_DEFAULT_USERNAME')
		print('    PY_IPFS_HTTP_CLIENT_DEFAULT_PASSWORD')
		print()
		print("!! Continuing without publishing to IPNS !!")
		print()

	return publish(
		ipns_key=ipns_key
	)


def publish(ipns_key: ty.Optional[str]) -> int:
	# Invoke Sphinx like the Makefile does
	result = sphinx.cmd.build.build_main([
		"-b", "html",
		"-d", "build/doctrees",
		".", "build/html",
		"-W", "--keep-going"
	])

	if result != 0:
		return result
	
	print()
	print(f"Exporting files to IPFS server at {ipfshttpclient.DEFAULT_ADDR}…")
	client = ipfshttpclient.connect()
	print('Adding files…')
	hash_docs = client.add("build/html", recursive=True, raw_leaves=True, pin=False)[-1]["Hash"]
	print('Getting directory hash…')
	hash_main = client.object.new("unixfs-dir")["Hash"]
	print('Getting docs hash…')
	hash_main = client.object.patch.add_link(hash_main, "docs", hash_docs)["Hash"]
	print(f'Pinning docs hash {hash_main}…')
	client.pin.add(hash_main)

	print("Final IPFS path:")
	print(f'  /ipfs/{hash_main}')
	print(f'  https://ipfs.io/ipfs/{hash_main}')
	
	if ipns_key:
		print()
		print("Exporting files to IPNS…")
		name_main = client.name.publish(hash_main, key=ipns_key)["Name"]
		print("Final IPNS path: /ipns/{0}".format(name_main))
		
		print()
		print("Run the following commandline on all systems that mirror this documentation:")
		print("  ipfs pin add {0} && ipfs name publish -k {1} /ipfs/{0}".format(hash_main, name_main))
	
	return 0


if __name__ == "__main__":
	sys.exit(main(sys.argv[1:]))
