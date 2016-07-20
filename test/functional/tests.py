# _*_ coding: utf-8 -*-
import os
import unittest

import ipfsApi


HERE = os.path.dirname(os.path.abspath(__file__))

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

    fake_lookup = dict((i['Name'], i['Hash']) for i in fake)

    ## test_add_multiple_from_list
    fake_file  = 'fake_dir/fsdfgh'
    fake_file_only_res = [{'Name': 'fsdfgh', 'Bytes': 8},
            {'Name': 'fsdfgh', 'Hash': 'QmQcCtMgLVwvMQGu6mvsRYLjwqrZJcYtH4mboM9urWW9vX'}]
    fake_file2 = 'fake_dir/popoiopiu'
    fake_files_res = [{'Name': 'fsdfgh', 'Bytes': 8},
            {'Name': 'fsdfgh', 'Hash': 'QmQcCtMgLVwvMQGu6mvsRYLjwqrZJcYtH4mboM9urWW9vX'},
            {'Name': 'popoiopiu', 'Bytes': 15},
            {'Name': 'popoiopiu', 'Hash': 'QmYAhvKYu46rh5NcHzeu6Bhc7NG9SqkF9wySj2jvB74Rkv'}]

    ## test_add_multiple_from_dirname
    fake_dir_test2 = 'fake_dir/test2'
    fake_dir_res = [{'Name': 'test2/fssdf', 'Bytes': 14},
            {'Name': 'test2/fssdf', 'Hash': 'Qmb1NPqPzdHCMvHRfCkk6TWLcnpGJ71KnafacCMm6TKLcD'},
            {'Name': 'test2/llllg', 'Bytes': 9},
            {'Name': 'test2/llllg', 'Hash': 'QmNuvmuFeeWWpxjCQwLkHshr8iqhGLWXFzSGzafBeawTTZ'},
            {'Name': 'test2', 'Hash': 'QmX1dd5DtkgoiYRKaPQPTCtXArUu4jEZ62rJBUcd5WhxAZ'}]

    ## test_add_recursive
    fake_dir = 'fake_dir'
    fake_dir_recursive_res = [{'Bytes': 8, 'Name': 'fake_dir/fsdfgh'},
            {'Hash': 'QmQcCtMgLVwvMQGu6mvsRYLjwqrZJcYtH4mboM9urWW9vX', 'Name': 'fake_dir/fsdfgh'},
            {'Bytes': 15, 'Name': 'fake_dir/popoiopiu'},
            {'Hash': 'QmYAhvKYu46rh5NcHzeu6Bhc7NG9SqkF9wySj2jvB74Rkv', 'Name': 'fake_dir/popoiopiu'},
            {'Bytes': 14, 'Name': 'fake_dir/test2/fssdf'},
            {'Hash': 'Qmb1NPqPzdHCMvHRfCkk6TWLcnpGJ71KnafacCMm6TKLcD', 'Name': 'fake_dir/test2/fssdf'},
            {'Bytes': 9, 'Name': 'fake_dir/test2/llllg'},
            {'Hash': 'QmNuvmuFeeWWpxjCQwLkHshr8iqhGLWXFzSGzafBeawTTZ', 'Name': 'fake_dir/test2/llllg'},
            {'Bytes': 8, 'Name': 'fake_dir/test3/ppppoooooooooo'},
            {'Hash': 'QmeMbJSHNCesAh7EeopackUdjutTJznum1Fn7knPm873Fe', 'Name': 'fake_dir/test3/ppppoooooooooo'},
            {'Hash': 'QmX1dd5DtkgoiYRKaPQPTCtXArUu4jEZ62rJBUcd5WhxAZ', 'Name': 'fake_dir/test2'},
            {'Hash': 'QmRphRr6ULDEj7YnXpLdnxhnPiVjv5RDtGX3er94Ec6v4Q', 'Name': 'fake_dir/test3'},
            {'Hash': 'QmYqqgRahxbZvudnzDu2ZzUS1vFSNEuCrxghM8hgT8uBFY', 'Name': 'fake_dir'}]

    def setUp(self):
        self._olddir = os.getcwd()
        os.chdir(HERE)

    def tearDown(self):
        os.chdir(self._olddir)

    #########
    # TESTS #
    #########

    def test_add_single_from_str(self):
        res = self.api.add(self.fake_file)
        self.assertEqual(res, self.fake_file_only_res)
    
    def test_add_single_from_fp(self):
        with open(self.fake_file, 'rb') as fp:
            res = self.api.add(fp)
            self.assertEqual(res, self.fake_file_only_res)
    
    def test_add_multiple_from_list(self):
        res = self.api.add([self.fake_file, self.fake_file2])
        self.assertEqual(res, self.fake_files_res)

    def test_add_multiple_from_dirname(self):
        res = self.api.add(self.fake_dir_test2)
        self.assertEqual(sorted(res,
                                key=lambda x: x['Name']),
                         sorted(self.fake_dir_res,
                                key=lambda x: x['Name']))


    def test_add_recursive(self):
        res = self.api.add(self.fake_dir, recursive=True)
        self.assertEqual(sorted(res,
                                key=lambda x: x['Name']),
                         sorted(self.fake_dir_recursive_res,
                                key=lambda x: x['Name']))

    def test_add_get_pyobject(self):
        data = [-1, 3.14, u'Hän€', b'23' ]
        res = self.api.add_pyobj(data)
        self.assertEqual(data,
                         self.api.get_pyobj(res))

class IpfsApiMFSTest(unittest.TestCase):
    
    test_files = {
        '/test_file1': {
            u'Name': u'fake_dir/popoiopiu',
            u'Stat': {u'Type': 'file',
                      u'Hash': 'QmUvobKqcCE56brA8pGTRRRsGy2SsDEKSxFLZkBQFv7Vvv',
                      u'Blocks': 1,
                      u'CumulativeSize': 73,
                      u'Size': 15}
        }
    }
    
    def setUp(self):
        self.api = ipfsApi.Client()
        self._olddir = os.getcwd()
        os.chdir(HERE)

    def tearDown(self):
        os.chdir(self._olddir)
    
    def test_write_stat_read_delete(self):
        for target, desc in self.test_files.items():
            # Create target file
            self.api.files_write(target, desc[u'Name'], opts={'create':True})
            
            # Verify stat information of file
            stat = self.api.files_stat(target)
            self.assertEqual(sorted(desc[u'Stat'].items()), sorted(stat.items()))
            
            # Read back (and compare file contents)
            with open(desc[u'Name'], 'r') as file:
                content = self.api.files_read(target)
                self.assertEqual(content, file.read())
            
            # Delete file
            self.api.files_rm(target)

            
class TestBlockFunctions(unittest.TestCase):
    def setUp(self):
        self.api = ipfsApi.Client()
        self.multihash = 'QmYA2fn8cMbVWo4v95RwcwJVyQsNtnEwHerfWR8UNtEwoE'
        self.content_size = 248

    def test_block_stat(self):
        expected_keys = ['Key', 'Size']
        res = self.api.block_stat(self.multihash)
        for key in expected_keys:
            self.assertTrue(key in res)

    def test_block_get(self):
        self.assertEqual(len(self.api.block_get(self.multihash)), self.content_size)

    def test_block_put(self):
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                            "functional", "fake_dir", "fsdfgh")
        expected_block_multihash = 'QmPevo2B1pwvDyuZyJbWVfhwkaGPee3f1kX36wFmqx1yna'
        expected_keys = ['Key', 'Size']
        res = self.api.block_put(path)
        for key in expected_keys:
            self.assertTrue(key in res)
        self.assertEqual(res['Key'], expected_block_multihash)

class TestObjectFunctions(unittest.TestCase):
    def setUp(self):
        self.api = ipfsApi.Client()

    def test_object_new(self):
        expected_keys = ['Hash']
        res = self.api.object_new()
        for key in expected_keys:
            self.assertTrue(key in res)



if __name__ == "__main__":
    unittest.main()
