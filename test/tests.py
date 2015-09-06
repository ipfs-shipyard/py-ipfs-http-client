import sys
sys.path.append('..')

import ipfsApi

if __name__ == "__main__":
    api = ipfsApi.Client()

    print api.add('fake_dir')
    print api.add('fake_dir', recursive=True)
