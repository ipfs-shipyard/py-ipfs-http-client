# _*_ coding: utf-8 -*-
import os
import shutil
import json
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
            {'Hash': u'QmRphRr6ULDEj7YnXpLdnxhnPiVjv5RDtGX3er94Ec6v4Q',
             'Name': 'fake_dir/test3'},
            {'Hash': u'QmYqqgRahxbZvudnzDu2ZzUS1vFSNEuCrxghM8hgT8uBFY',
             'Name': 'fake_dir'}]

    fake_lookup = dict((i['Name'], i['Hash']) for i in fake)

    ## test_add_multiple_from_list
    fake_file  = 'fake_dir/fsdfgh'
    fake_file_only_res = {'Name': 'fsdfgh',
                          'Hash': 'QmQcCtMgLVwvMQGu6mvsRYLjwqrZJcYtH4mboM9urWW9vX'}
    fake_file2 = 'fake_dir/popoiopiu'
    fake_files_res = [
            {'Name': 'fsdfgh', 'Hash': 'QmQcCtMgLVwvMQGu6mvsRYLjwqrZJcYtH4mboM9urWW9vX'},
            {'Name': 'popoiopiu', 'Hash': 'QmYAhvKYu46rh5NcHzeu6Bhc7NG9SqkF9wySj2jvB74Rkv'}]

    ## test_add_multiple_from_dirname
    fake_dir_test2 = 'fake_dir/test2'
    fake_dir_res = [
            {'Name': 'test2/fssdf', 'Hash': 'Qmb1NPqPzdHCMvHRfCkk6TWLcnpGJ71KnafacCMm6TKLcD'},
            {'Name': 'test2/llllg', 'Hash': 'QmNuvmuFeeWWpxjCQwLkHshr8iqhGLWXFzSGzafBeawTTZ'},
            {'Name': 'test2', 'Hash': 'QmX1dd5DtkgoiYRKaPQPTCtXArUu4jEZ62rJBUcd5WhxAZ'}]

    ## test_add_recursive
    fake_dir = 'fake_dir'
    fake_dir_recursive_res = [
            {'Hash': 'QmQcCtMgLVwvMQGu6mvsRYLjwqrZJcYtH4mboM9urWW9vX', 'Name': 'fake_dir/fsdfgh'},
            {'Hash': 'QmYAhvKYu46rh5NcHzeu6Bhc7NG9SqkF9wySj2jvB74Rkv', 'Name': 'fake_dir/popoiopiu'},
            {'Hash': 'Qmb1NPqPzdHCMvHRfCkk6TWLcnpGJ71KnafacCMm6TKLcD', 'Name': 'fake_dir/test2/fssdf'},
            {'Hash': 'QmNuvmuFeeWWpxjCQwLkHshr8iqhGLWXFzSGzafBeawTTZ', 'Name': 'fake_dir/test2/llllg'},
            {'Hash': 'QmeMbJSHNCesAh7EeopackUdjutTJznum1Fn7knPm873Fe', 'Name': 'fake_dir/test3/ppppoooooooooo'},
            {'Hash': 'QmX1dd5DtkgoiYRKaPQPTCtXArUu4jEZ62rJBUcd5WhxAZ', 'Name': 'fake_dir/test2'},
            {'Hash': 'QmRphRr6ULDEj7YnXpLdnxhnPiVjv5RDtGX3er94Ec6v4Q', 'Name': 'fake_dir/test3'},
            {'Hash': 'QmYqqgRahxbZvudnzDu2ZzUS1vFSNEuCrxghM8hgT8uBFY', 'Name': 'fake_dir'}]

    ## test_refs
    refs_res = [{'Err': '', 'Ref': 'QmQcCtMgLVwvMQGu6mvsRYLjwqrZJcYtH4mboM9urWW9vX'},
                {'Err': '', 'Ref': 'QmYAhvKYu46rh5NcHzeu6Bhc7NG9SqkF9wySj2jvB74Rkv'},
                {'Err': '', 'Ref': 'QmX1dd5DtkgoiYRKaPQPTCtXArUu4jEZ62rJBUcd5WhxAZ'},
                {'Err': '', 'Ref': 'QmRphRr6ULDEj7YnXpLdnxhnPiVjv5RDtGX3er94Ec6v4Q'}]

    def setUp(self):
        self._olddir = os.getcwd()
        os.chdir(HERE)

    def tearDown(self):
        os.chdir(self._olddir)

    #########
    # TESTS #
    #########

    def test_version(self):
        expected = ['Repo', 'Commit', 'Version']
        resp_version = self.api.version()
        for key in expected:
            self.assertTrue(key in resp_version)

    def test_id(self):
        expected = ['PublicKey', 'ProtocolVersion',
                    'ID', 'AgentVersion', 'Addresses']
        resp_id = self.api.id()
        for key in expected:
            self.assertTrue(key in resp_id)

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

    def test_get_file(self):
        self.api.add(self.fake_file)

        test_hash = self.fake[0]['Hash']

        self.api.get(test_hash)
        self.assertIn(test_hash, os.listdir(os.getcwd()))

        os.remove(test_hash)
        self.assertNotIn(test_hash, os.listdir(os.getcwd()))

    def test_get_dir(self):
        self.api.add(self.fake_dir, recursive=True)

        test_hash = self.fake[8]['Hash']

        self.api.get(test_hash)
        self.assertIn(test_hash, os.listdir(os.getcwd()))

        shutil.rmtree(test_hash)
        self.assertNotIn(test_hash, os.listdir(os.getcwd()))

    def test_get_path(self):
        self.api.add(self.fake_file)

        test_hash = self.fake[8]['Hash'] + '/fsdfgh'

        self.api.get(test_hash)
        self.assertIn('fsdfgh', os.listdir(os.getcwd()))

        os.remove('fsdfgh')
        self.assertNotIn('fsdfgh', os.listdir(os.getcwd()))

    def test_refs(self):
        self.api.add(self.fake_dir, recursive=True)

        refs = self.api.refs(self.fake[8]['Hash'])

        self.assertEqual(sorted(refs, key=lambda x: x['Ref']),
                         sorted(self.refs_res, key=lambda x: x['Ref']))

    def test_refs_local(self):
        refs = self.api.refs_local()

        self.assertEqual(sorted(refs[0].keys()), ['Err', 'Ref'])

    def test_cat_single_file_str(self):
        self.api.add(self.fake_file)
        res = self.api.cat('QmQcCtMgLVwvMQGu6mvsRYLjwqrZJcYtH4mboM9urWW9vX')
        self.assertEqual("dsadsad\n", res)


class IpfsApiLogTest(unittest.TestCase):

    def setUp(self):
        self.api = ipfsApi.Client()

    def test_log_ls_level(self):
        """
        Unfortunately there is no way of knowing the logging levels prior
        to this test. This makes it impossible to guarantee that the logging
        levels are the same as before the test was run.
        """
        # Retrieves the list of logging subsystems for a running daemon.
        resp_ls = self.api.log_ls()
        # The response should be a dictionary with only one key ('Strings').
        self.assertTrue('Strings' in resp_ls)

        # Sets the logging level to 'error' for the first subsystem found.
        sub = resp_ls['Strings'][0]
        resp_level = self.api.log_level(sub, 'error')
        self.assertEqual(resp_level['Message'],
                         "Changed log level of \'%s\' to 'error'\n" % sub)

    def test_log_tail(self):
        # Gets the response object.
        tail = self.api.log_tail()

        # Takes the first log received.
        line = tail.readline()
        log = json.loads(line.decode())

        # Closes the response object.
        tail.close()

        # The log should have been parsed into a dictionary object with
        # various keys depending on the event that occured.
        self.assertTrue(type(log) is dict)


class IpfsApiPinTest(unittest.TestCase):

    fake_dir_hash = 'QmYqqgRahxbZvudnzDu2ZzUS1vFSNEuCrxghM8hgT8uBFY'

    def setUp(self):
        self.api = ipfsApi.Client()
        # Add resources to be pinned.
        self.resource = self.api.add_str(u'Mary had a little lamb')
        resp_add = self.api.add('fake_dir', recursive=True)
        self.fake_dir_hashes = [el['Hash'] for el in resp_add if 'Hash' in el]

    def test_pin_ls_add_rm_single(self):
        # Get pinned objects at start.
        pins_begin = self.api.pin_ls()['Keys']

        # Unpin the resource if already pinned.
        if self.resource in pins_begin.keys():
            self.api.pin_rm(self.resource)

        # No matter what, the resource should not be pinned at this point.
        self.assertFalse(self.resource in self.api.pin_ls()['Keys'])

        for option in [True, False]:
            # Pin the resource.
            resp_add = self.api.pin_add(self.resource,
                                        opts={"recursive":str(option)})
            pins_afer_add = self.api.pin_ls()['Keys']
            self.assertEqual(resp_add['Pins'], [self.resource])
            self.assertTrue(self.resource in pins_afer_add)
            self.assertEqual(pins_afer_add[self.resource]['Type'] == 'recursive',
                             option)

            # Unpin the resource.
            resp_rm = self.api.pin_rm(self.resource)
            pins_afer_rm = self.api.pin_ls()['Keys']
            self.assertEqual(resp_rm['Pins'], [self.resource])
            self.assertFalse(self.resource in pins_afer_rm)

        # Get pinned objects at end.
        pins_end = self.api.pin_ls()['Keys']

        # Compare pinned items from start to finish of test.
        self.assertFalse(self.resource in pins_end.keys())

    def test_pin_ls_add_rm_directory(self):
        # Get pinned objects at start.
        pins_begin = self.api.pin_ls()['Keys']

        # Remove fake_dir if it had previously been pinned.
        if self.fake_dir_hash in pins_begin.keys() and \
           pins_begin[self.fake_dir_hash]['Type'] == 'recursive':
            self.api.pin_rm(self.fake_dir_hash)

        # Make sure I removed it
        pins_after_rm = self.api.pin_ls()['Keys']
        self.assertFalse(self.fake_dir_hash in pins_after_rm.keys() and \
                        pins_after_rm[self.fake_dir_hash]['Type'] == 'recursive')

        # Add 'fake_dir' recursively.
        self.api.pin_add(self.fake_dir_hash)

        # Make sure all appear on the list of pinned objects.
        pins_after_add = self.api.pin_ls()['Keys'].keys()
        for el in self.fake_dir_hashes:
            self.assertTrue(el in pins_after_add)

        # Clean up.
        self.api.pin_rm(self.fake_dir_hash)
        pins_end = self.api.pin_ls()['Keys'].keys()
        self.assertFalse(self.fake_dir_hash in pins_end and \
                        pins_after_rm[self.fake_dir_hash]['Type'] == 'recursive')


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
            self.assertEqual(sorted(desc[u'Stat'].items()),
                             sorted(stat.items()))

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


class IpfsApiRepoTest(unittest.TestCase):

    def setUp(self):
        self.api = ipfsApi.Client()

    def test_repo_stat(self):
        # Verify that the correct key-value pairs are returned
        stat = self.api.repo_stat()
        self.assertEqual(sorted(stat.keys()), ['NumObjects', 'RepoPath',
                                               'RepoSize', 'Version'])

    def test_repo_gc(self):
        # Add and unpin an object to be garbage collected
        garbage = self.api.add_str('Test String')
        self.api.pin_rm(garbage)

        # Collect the garbage object with object count before and after
        orig_objs = self.api.repo_stat()['NumObjects']
        gc = self.api.repo_gc()
        cur_objs = self.api.repo_stat()['NumObjects']

        # Verify the garbage object was collected
        self.assertGreater(orig_objs, cur_objs)
        keys = [el['Key'] for el in gc]
        self.assertTrue(garbage in keys)


class IpfsApiObjectTest(unittest.TestCase):

    def setUp(self):
        self.api = ipfsApi.Client()
        self._olddir = os.getcwd()
        os.chdir(HERE)
        # Add a resource to get the stats for.
        self.resource = self.api.add_str(u'Mary had a little lamb')

    def tearDown(self):
        os.chdir(self._olddir)

    def test_object_new(self):
        expected_keys = ['Hash']
        res = self.api.object_new()
        for key in expected_keys:
            self.assertTrue(key in res)

    def test_object_stat(self):
        expected = ['Hash', 'CumulativeSize', 'DataSize',
                    'NumLinks', 'LinksSize', 'BlockSize']
        resp_stat = self.api.object_stat(self.resource)
        for key in expected:
            self.assertTrue(key in resp_stat)

    def test_object_put_get(self):
        # Set paths to test json files
        path_no_links = os.path.join(os.path.dirname(__file__),
                                     "fake_json", "no_links.json")
        path_links = os.path.join(os.path.dirname(__file__),
                                  "fake_json", "links.json")

        # Put the json objects on the DAG
        no_links = self.api.object_put(path_no_links)
        links = self.api.object_put(path_links)

        # Verify the correct content was put
        self.assertEqual(no_links['Hash'], 'QmXg9Pp2ytZ14xgmQjYEiHjVjMFXzCVVEcRTWJBmLgR39V')
        self.assertEqual(links['Hash'], 'QmZZmY4KCu9r3e7M2Pcn46Fc5qbn6NpzaAGaYb22kbfTqm')
        self.assertEqual(links['Links'][0]['Hash'], 'QmXg9Pp2ytZ14xgmQjYEiHjVjMFXzCVVEcRTWJBmLgR39V')

        # Get the objects from the DAG
        get_no_links = self.api.object_get('QmXg9Pp2ytZ14xgmQjYEiHjVjMFXzCVVEcRTWJBmLgR39V')
        get_links = self.api.object_get('QmZZmY4KCu9r3e7M2Pcn46Fc5qbn6NpzaAGaYb22kbfTqm')

        # Verify the objects we put have been gotten
        self.assertEqual(get_no_links['Data'], 'abc')
        self.assertEqual(get_links['Data'], 'another')
        self.assertEqual(get_links['Links'][0]['Name'], 'some link')

    def test_object_links(self):
        # Set paths to test json files
        path_links = os.path.join(os.path.dirname(__file__),
                                  "fake_json", "links.json")

        # Put json object on the DAG and get its links
        self.api.object_put(path_links)
        links = self.api.object_links('QmZZmY4KCu9r3e7M2Pcn46Fc5qbn6NpzaAGaYb22kbfTqm')

        # Verify the correct link has been gotten
        self.assertEqual(links['Links'][0]['Hash'], 'QmXg9Pp2ytZ14xgmQjYEiHjVjMFXzCVVEcRTWJBmLgR39V')

    def test_object_data(self):
        # Set paths to test json files
        path_links = os.path.join(os.path.dirname(__file__),
                                  "fake_json", "links.json")

        # Put json objects on the DAG and get its data
        self.api.object_put(path_links)
        data = self.api.object_data('QmZZmY4KCu9r3e7M2Pcn46Fc5qbn6NpzaAGaYb22kbfTqm')

        # Verify the correct bytes have been gotten
        self.assertEqual(data, 'another')

    def test_object_patch_append_data(self):
        """Warning, this test depends on the contents of
            test/functional/fake_dir/fsdfgh
        """
        result = self.api.object_patch_append_data(
                'QmdfTbBqBPQ7VNxZEYEj14VmRuZBkqFbiwReogJgS1zR1n', 'fake_dir/fsdfgh')
        self.assertEqual(result,
                {'Hash': 'QmcUsyoGVxWoQgYKgmLaDBGm8J3eHWfchMh3oDUD5FrrtN'})

    def test_object_patch_add_link(self):
        """Warning, this test depends on the contents of
            test/functional/fake_dir/fsdfgh
        """
        result = self.api.object_patch_add_link(
                'QmdfTbBqBPQ7VNxZEYEj14VmRuZBkqFbiwReogJgS1zR1n', 'self',
                'QmdfTbBqBPQ7VNxZEYEj14VmRuZBkqFbiwReogJgS1zR1n')
        self.assertEqual(result,
                {'Hash': 'QmbWSr7YXBLcF23VVb7yPvUuogUPn46GD7gXftXC6mmsNM'})

    def test_object_patch_rm_link(self):
        """Warning, this test depends on the contents of
            test/functional/fake_dir/fsdfgh
        """
        result = self.api.object_patch_rm_link(
                'QmbWSr7YXBLcF23VVb7yPvUuogUPn46GD7gXftXC6mmsNM', 'self')
        self.assertEqual(result,
                {'Hash': 'QmdfTbBqBPQ7VNxZEYEj14VmRuZBkqFbiwReogJgS1zR1n'})

    def test_object_patch_set_data(self):
        """Warning, this test depends on the contents of
            test/functional/fake_dir/popoiopiu
        """
        result = self.api.object_patch_set_data(
                'QmdfTbBqBPQ7VNxZEYEj14VmRuZBkqFbiwReogJgS1zR1n', 'fake_dir/popoiopiu')
        self.assertEqual(result,
                {'Hash': 'QmV4QR7MCBj5VTi6ddHmXPyjWGzbaKEtX2mx7axA5PA13G'})

if __name__ == "__main__":
    unittest.main()
