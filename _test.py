import ipfsApi
from pprint import pprint
c = ipfsApi.Client()
pprint(c.add('test/functional', recursive=True))
