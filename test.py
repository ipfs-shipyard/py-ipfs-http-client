import ipfs


if __name__ == "__main__":
    api = ipfs.Client()

    #print api.swarm_peers()
    #print api.cat('Qmf3sE2DaCSEc9XVr9yro9Y4Sj5Ac8rgjqqWYAsC2c9FrV')

    test_json = {'dsadsd': ['dsdsad', 'dsadsad', 'dsdsad']}

    res = api.add_json(test_json)
    print res
    print api.load_json(res)

    print

    print api.add_dir('test')
