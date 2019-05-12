#!/usr/bin/python3
import os
import sys
__dir__ = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(__dir__, ".."))

import sphinx.cmd.build
import ipfshttpclient

# Ensure working directory is script directory
os.chdir(__dir__)

def main(argv=sys.argv[1:], program=sys.argv[0]):
	if len(argv) != 1:
		print("Usage: {0} [IPNS-key]".format(os.path.basename(program)))
		print()
		print("!! Continuing without publishing to IPNS !!")
		print()
	
	# Invoke Sphinx like the Makefile does
	result = sphinx.cmd.build.build_main(["-b", "html", "-d", "build/doctrees", ".", "build/html"])
	if result != 0:
		return result
	
	print()
	print("Exporting files to IPFS…")
	client = ipfshttpclient.connect()
	hash_docs = client.add("build/html", recursive=True, raw_leaves=True, pin=False)[-1]["Hash"]
	hash_main = client.object.new("unixfs-dir")["Hash"]
	hash_main = client.object.patch.add_link(hash_main, "docs", hash_docs)["Hash"]
	client.pin.add(hash_main)
	print("Final IPFS path: /ipfs/{0}".format(hash_main))
	
	if len(argv) == 1:
		key = argv[0]
		print()
		print("Exporting files to IPNS…")
		name_main = client.name.publish(hash_main, key=key)["Name"]
		print("Final IPNS path: /ipns/{0}".format(name_main))
		
		print()
		print("Run the following commandline on all systems that mirror this documentation:")
		print("  ipfs pin add {0} && ipfs name publish -k {1} /ipfs/{0}".format(hash_main, name_main))
	
	return 0

if __name__ == "__main__":
	sys.exit(main())