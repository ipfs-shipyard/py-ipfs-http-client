import sys
sys.path.append('..')

import ipfsApi

fake_dir = [{'Hash': u'QmQcCtMgLVwvMQGu6mvsRYLjwqrZJcYtH4mboM9urWW9vX',
             'Name': 'fake_dir/fsdfgh'},
            {'Hash': u'QmYAhvKYu46rh5NcHzeu6Bhc7NG9SqkF9wySj2jvB74Rkv',
             'Name': 'fake_dir/popoiopiu'},
            {'Hash': u'QmeMbJSHNCesAh7EeopackUdjutTJznum1Fn7knPm873Fe',
             'Name': 'fake_dir/test3/ppppoooooooooo'},
            {'Hash': u'QmRphRr6ULDEj7YnXpLdnxhnPiVjv5RDtGX3er94Ec6v4Q',
             'Name': 'fake_dir/test3'},
            {'Hash': u'QmNuvmuFeeWWpxjCQwLkHshr8iqhGLWXFzSGzafBeawTTZ',
             'Name': 'fake_dir/test2/llllg'},
            {'Hash': u'Qmb1NPqPzdHCMvHRfCkk6TWLcnpGJ71KnafacCMm6TKLcD',
             'Name': 'fake_dir/test2/fssdf'},
            {'Hash': u'QmX1dd5DtkgoiYRKaPQPTCtXArUu4jEZ62rJBUcd5WhxAZ',
             'Name': 'fake_dir/test2'},
            {'Hash': u'QmbZuss6aAizLEAt2Jt2BD29oq4XfMieGezi6mN4vz9g9A',
             'Name': 'fake_dir'}]

fake_dir_lookup = {i['Name']: i['Hash'] for i in fake_dir}


if __name__ == "__main__":
    api = ipfsApi.Client()
    
    test_file = 'fake_dir/fsdfgh'
    test_file2 = 'fake_dir/popoiopiu'

    ## api.add ##
    res = api.add(test_file)
    assert res[u"Hash"] == fake_dir_lookup[test_file]
    
    res = api.add(['fake_dir/fsdfgh', 'fake_dir/popoiopiu'])
    assert res == [{u'Hash': u'QmQcCtMgLVwvMQGu6mvsRYLjwqrZJcYtH4mboM9urWW9vX',
                    u'Name': u'fsdfgh'},
                   {u'Hash': u'QmYAhvKYu46rh5NcHzeu6Bhc7NG9SqkF9wySj2jvB74Rkv',
                    u'Name': u'popoiopiu'},
                   {u'Hash': u'QmVkNdzCBukBRdpyFiKPyL2R15qPExMr9rV9RFV2kf9eeV', u'Name': u''}]
    
    res = api.add('fake_dir/test2')
    assert res == [{u'Hash': u'QmNuvmuFeeWWpxjCQwLkHshr8iqhGLWXFzSGzafBeawTTZ',
                    u'Name': u'llllg'},
                   {u'Hash': u'Qmb1NPqPzdHCMvHRfCkk6TWLcnpGJ71KnafacCMm6TKLcD',
                    u'Name': u'fssdf'},
                   {u'Hash': u'QmX1dd5DtkgoiYRKaPQPTCtXArUu4jEZ62rJBUcd5WhxAZ', u'Name': u''}]

    print api.add('fake_dir')
    print api.add('fake_dir', recursive=True)
