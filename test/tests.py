import unittest

import sys
sys.path.append('..')

import ipfsApi


class IpfsApiTest(unittest.TestCase):

    api = ipfsApi.Client()
    
    fake = [{'Hash': u'QmQcCtMgLVwvMQGu6mvsRYLjwqrZJcYtH4mboM9urWW9vX',
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

    fake_lookup = {i['Name']: i['Hash'] for i in fake}
  

    ## test_add_multiple_from_list
    fake_file  = 'fake_dir/fsdfgh'
    fake_file2 = 'fake_dir/popoiopiu'
    fake_files_res = [{u'Hash': u'QmQcCtMgLVwvMQGu6mvsRYLjwqrZJcYtH4mboM9urWW9vX',
                       u'Name': u'fsdfgh'},
                      {u'Hash': u'QmYAhvKYu46rh5NcHzeu6Bhc7NG9SqkF9wySj2jvB74Rkv',
                       u'Name': u'popoiopiu'},
                      {u'Hash': u'QmVkNdzCBukBRdpyFiKPyL2R15qPExMr9rV9RFV2kf9eeV',
                       u'Name': u''}]
    
    ## test_add_multiple_from_dirname
    fake_dir = 'fake_dir/test2'
    fake_dir_res = [{u'Hash': u'QmNuvmuFeeWWpxjCQwLkHshr8iqhGLWXFzSGzafBeawTTZ',
                     u'Name': u'llllg'},
                    {u'Hash': u'Qmb1NPqPzdHCMvHRfCkk6TWLcnpGJ71KnafacCMm6TKLcD',
                     u'Name': u'fssdf'},
                    {u'Hash': u'QmX1dd5DtkgoiYRKaPQPTCtXArUu4jEZ62rJBUcd5WhxAZ',
                     u'Name': u''}]


    #########
    # TESTS #
    #########

    def test_add_single_from_str(self):
        res = self.api.add(self.fake_file)
        self.assertEqual(res[u"Hash"], self.fake_lookup[self.fake_file])
    
    def test_add_single_from_fp(self):
        with open(self.fake_file, 'rb') as fp:
            res = self.api.add(fp)
            self.assertEqual(res[u"Hash"], self.fake_lookup[self.fake_file])
    
    def test_add_multiple_from_list(self):
        res = self.api.add([self.fake_file, self.fake_file2])
        self.assertEqual(res, self.fake_files_res)

    def test_add_multiple_from_dirname(self):
        res = self.api.add(self.fake_dir)
        self.assertEqual(res, self.fake_dir_res)

    def test_add_recursive(self):
        pass



if __name__ == "__main__":
    unittest.main()
