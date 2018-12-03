# _*_ coding: utf-8 -*-
import os
import json
import shutil
import socket
import sys
import time
import unittest
import logging
import uuid

import pytest

import ipfshttpclient


__is_available = None
def is_available():
    """
    Return whether the IPFS daemon is reachable or not
    """
    global __is_available

    if not isinstance(__is_available, bool):
        try:
            ipfshttpclient.connect()
        except ipfshttpclient.exceptions.Error as error:
            __is_available = False

            # Make sure version incompatiblity is displayed to the user
            if isinstance(error, ipfshttpclient.exceptions.VersionMismatch):
                raise
        else:
            __is_available = True

    return __is_available


def skipIfOffline():
    if is_available():
        return lambda func: func
    else:
        return unittest.skip("IPFS node is not available")

def skipUnlessCI():
    have_ci  = os.environ.get("CI", "false") == "true"
    have_pid = os.environ.get("PY_IPFS_HTTP_CLIENT_TEST_DAEMON_PID", "").isdigit()
    return unittest.skipUnless(have_ci and have_pid, "CI-only test")


def test_ipfs_node_available():
    addr = "[{0}]:{1}".format(ipfshttpclient.DEFAULT_HOST, ipfshttpclient.DEFAULT_PORT)
    assert is_available(), "Functional tests require an IPFS node to be available at: " + addr



HERE = os.path.dirname(os.path.abspath(__file__))

class AssertVersionTest(unittest.TestCase):
    def test_assert_version(self):
        # Minimum required version
        ipfshttpclient.assert_version("0.1.0", "0.1.0", "0.2.0")

        # Too high version
        with self.assertRaises(ipfshttpclient.exceptions.VersionMismatch):
            ipfshttpclient.assert_version("0.2.0", "0.1.0", "0.2.0")

        # Too low version
        with self.assertRaises(ipfshttpclient.exceptions.VersionMismatch):
            ipfshttpclient.assert_version("0.0.5", "0.1.0", "0.2.0")

@skipIfOffline()
class IpfsHttpClientTest(unittest.TestCase):

    http_client = ipfshttpclient.Client()

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
            {'Hash': u'QmNx8xVu9mpdz9k6etbh2S8JwZygatsZVCH4XhgtfUYAJi',
             'Name': 'fake_dir'}]

    fake_lookup = dict((i['Name'], i['Hash']) for i in fake)

    ## test_add_multiple_from_list
    fake_file  = 'fake_dir/fsdfgh'
    fake_file_only_res = {'Hash': 'QmQcCtMgLVwvMQGu6mvsRYLjwqrZJcYtH4mboM9urWW9vX',
                          'Name': 'fsdfgh', 'Size': '16'}
    fake_file_dir_res = [
        {'Hash': 'QmQcCtMgLVwvMQGu6mvsRYLjwqrZJcYtH4mboM9urWW9vX',
         'Name': 'fsdfgh', 'Size': '16'},
        {'Hash': 'Qme7vmxd4LAAYL7vpho3suQeT3gvMeLLtPdp7myCb9Db55',
         'Name': '',       'Size': '68'}
    ]
    fake_file2 = 'fake_dir/popoiopiu'
    fake_files_res = [
            {'Hash': 'QmQcCtMgLVwvMQGu6mvsRYLjwqrZJcYtH4mboM9urWW9vX',
             'Name': 'fsdfgh',    'Size': '16'},
            {'Hash': 'QmYAhvKYu46rh5NcHzeu6Bhc7NG9SqkF9wySj2jvB74Rkv',
             'Name': 'popoiopiu', 'Size': '23'}]

    ## test_add_multiple_from_dirname
    fake_dir_test2 = 'fake_dir/test2'
    fake_dir_res = [
            {'Hash': 'QmStL6TPbJfMHQhHjoVT93kCynVx3GwLf7xwgrtScqABhU',
             'Name': 'test2',                 'Size': '297'},
            {'Hash': 'QmV3n14G8iQoNG8zpHCUZnmQpcQbhEfhQZ8NHvUEdoiXAN',
             'Name': 'test2/high',            'Size': '114'},
            {'Hash': 'QmZazHsY4nbhRTHTEp5SUWd4At6aSXia1kxEuywHTicayE',
             'Name': 'test2/high/five',       'Size': '64'},
            {'Hash': 'QmW8tRcpqy5siMNAU9Lx3GADAxQbVUrx8XJGFDjkd6vqLT',
             'Name': 'test2/high/five/dummy', 'Size': '13'},
            {'Hash': 'Qmb1NPqPzdHCMvHRfCkk6TWLcnpGJ71KnafacCMm6TKLcD',
             'Name': 'test2/fssdf',           'Size': '22'},
            {'Hash': 'QmNuvmuFeeWWpxjCQwLkHshr8iqhGLWXFzSGzafBeawTTZ',
             'Name': 'test2/llllg',           'Size': '17'}]

    ## test_add_filepattern_from_dirname
    pattern = '**/fss*'
    # the hash of the folder is not same as above because the content of the folder
    # added is not same.
    fake_dir_fnpattern_res = [
            {'Name': 'fake_dir/test2/fssdf', 'Hash': 'Qmb1NPqPzdHCMvHRfCkk6TWLcnpGJ71KnafacCMm6TKLcD', 'Size': '22'},
            {'Name': 'fake_dir/test2',       'Hash': 'QmT5rV6EsKNSW619SntLrkCxbUXXQh4BrKm3JazF2zEgEe', 'Size': '73'},
            {'Name': 'fake_dir',             'Hash': 'QmbPzQruAEFjUU3gQfupns6b8USr8VrD9H71GrqGDXQSxm', 'Size': '124'}]

    ## test_add_filepattern_subdir_wildcard
    pattern2 = 'test2/**/high'
    fake_dir_fnpattern2_res = [
            {'Hash': 'QmUXuNHpV6cdeTngSkEMbP2nQDPuyE2MFXNYtTXzZvLZHf',
             'Name': 'fake_dir',                       'Size': '216'},
            {'Hash': 'QmZGuwqaXMmSwJcfTsvseHwy3mvDPD9zrs9WVowAZcQN4W',
             'Name': 'fake_dir/test2',                 'Size': '164'},
            {'Hash': 'QmV3n14G8iQoNG8zpHCUZnmQpcQbhEfhQZ8NHvUEdoiXAN',
             'Name': 'fake_dir/test2/high',            'Size': '114'},
            {'Hash': 'QmZazHsY4nbhRTHTEp5SUWd4At6aSXia1kxEuywHTicayE',
             'Name': 'fake_dir/test2/high/five',       'Size': '64'},
            {'Hash': 'QmW8tRcpqy5siMNAU9Lx3GADAxQbVUrx8XJGFDjkd6vqLT',
             'Name': 'fake_dir/test2/high/five/dummy', 'Size': '13'}]


    ## test_add_recursive
    fake_dir = 'fake_dir'
    fake_dir_recursive_res = [
            {'Hash': 'QmNx8xVu9mpdz9k6etbh2S8JwZygatsZVCH4XhgtfUYAJi',
             'Name': 'fake_dir',                       'Size': '610'},
            {'Hash': 'QmQcCtMgLVwvMQGu6mvsRYLjwqrZJcYtH4mboM9urWW9vX',
             'Name': 'fake_dir/fsdfgh',                'Size': '16'},
            {'Hash': 'QmYAhvKYu46rh5NcHzeu6Bhc7NG9SqkF9wySj2jvB74Rkv',
             'Name': 'fake_dir/popoiopiu',             'Size': '23'},
            {'Hash': 'QmStL6TPbJfMHQhHjoVT93kCynVx3GwLf7xwgrtScqABhU',
             'Name': 'fake_dir/test2',                 'Size': '297'},
            {'Hash': 'Qmb1NPqPzdHCMvHRfCkk6TWLcnpGJ71KnafacCMm6TKLcD',
             'Name': 'fake_dir/test2/fssdf',           'Size': '22'},
            {'Hash': 'QmV3n14G8iQoNG8zpHCUZnmQpcQbhEfhQZ8NHvUEdoiXAN',
             'Name': 'fake_dir/test2/high',            'Size': '114'},
            {'Hash': 'QmZazHsY4nbhRTHTEp5SUWd4At6aSXia1kxEuywHTicayE',
             'Name': 'fake_dir/test2/high/five',       'Size': '64'},
            {'Hash': 'QmW8tRcpqy5siMNAU9Lx3GADAxQbVUrx8XJGFDjkd6vqLT',
             'Name': 'fake_dir/test2/high/five/dummy', 'Size': '13'},
            {'Hash': 'QmNuvmuFeeWWpxjCQwLkHshr8iqhGLWXFzSGzafBeawTTZ',
             'Name': 'fake_dir/test2/llllg',           'Size': '17'},
            {'Hash': 'QmRphRr6ULDEj7YnXpLdnxhnPiVjv5RDtGX3er94Ec6v4Q',
             'Name': 'fake_dir/test3',                 'Size': '76'},
            {'Hash': 'QmeMbJSHNCesAh7EeopackUdjutTJznum1Fn7knPm873Fe',
             'Name': 'fake_dir/test3/ppppoooooooooo',  'Size': '16'}]

    ## test_refs
    refs_res = [{'Err': '', 'Ref': 'QmQcCtMgLVwvMQGu6mvsRYLjwqrZJcYtH4mboM9urWW9vX'},
                {'Err': '', 'Ref': 'QmYAhvKYu46rh5NcHzeu6Bhc7NG9SqkF9wySj2jvB74Rkv'},
                {'Err': '', 'Ref': 'QmStL6TPbJfMHQhHjoVT93kCynVx3GwLf7xwgrtScqABhU'},
                {'Err': '', 'Ref': 'QmRphRr6ULDEj7YnXpLdnxhnPiVjv5RDtGX3er94Ec6v4Q'}]

    def setUp(self):
        self._olddir = os.getcwd()
        os.chdir(HERE)

        # Makes all of the diff visible if the hashes change for some reason
        self.maxDiff = None
        
        self.pinned = set(self.http_client.pin_ls(type="recursive")["Keys"])

    def tearDown(self):
        os.chdir(self._olddir)

    def _clean_up_pins(self):
        for multihash in self.http_client.pin_ls(type="recursive")["Keys"]:
            if multihash not in self.pinned:
                self.http_client.pin_rm(multihash)
    
    @staticmethod
    def _sort_by_key(items, key="Name"):
        return sorted(items, key=lambda x: x[key])

    #########
    # TESTS #
    #########

    def test_version(self):
        expected = ['Repo', 'Commit', 'Version']
        resp_version = self.http_client.version()
        for key in expected:
            assert key in resp_version

    def test_id(self):
        expected = ['PublicKey', 'ProtocolVersion',
                    'ID', 'AgentVersion', 'Addresses']
        resp_id = self.http_client.id()
        for key in expected:
            assert key in resp_id

    def test_add_single_from_str(self):
        res = self.http_client.add(self.fake_file, pin=False)
        
        assert self.fake_file_only_res == res
        
        assert res["Hash"] not in self.http_client.pin_ls(type="recursive")
        assert res["Hash"]     in list(map(lambda i: i["Ref"], self.http_client.refs_local()))

    def test_add_single_from_fp(self):
        with open(self.fake_file, 'rb') as fp:
            res = self.http_client.add(fp, pin=False)
            
            assert self.fake_file_only_res == res
            
            assert res["Hash"] not in self.http_client.pin_ls(type="recursive")
            assert res["Hash"]     in list(map(lambda i: i["Ref"], self.http_client.refs_local()))

    def test_add_single_from_str_with_dir(self):
        res = self.http_client.add(self.fake_file, wrap_with_directory=True)
        
        try:
            assert self.fake_file_dir_res == res
            
            dir_hash = None
            for item in res:
                if item["Name"] == "":
                    dir_hash = item["Hash"]
            assert dir_hash in self.http_client.pin_ls(type="recursive")["Keys"]
        finally:
            self._clean_up_pins()

    def test_only_hash_file(self):
        self.http_client.repo_gc()
        
        res = self.http_client.add(self.fake_file, only_hash=True)
        
        assert self.fake_file_only_res == res
        
        assert res["Hash"] not in self.http_client.pin_ls(type="recursive")
        assert res["Hash"] not in list(map(lambda i: i["Ref"], self.http_client.refs_local()))

    def test_add_multiple_from_list(self):
        res = self.http_client.add([self.fake_file, self.fake_file2])
        
        try:
            assert self.fake_files_res == res
        finally:
            self._clean_up_pins()

    def test_add_multiple_from_dirname(self):
        res = self.http_client.add(self.fake_dir_test2)
        
        try:
            assert self._sort_by_key(self.fake_dir_res) == self._sort_by_key(res)
        finally:
            self._clean_up_pins()

    def test_add_filepattern_from_dirname(self):
        res = self.http_client.add(self.fake_dir, pattern=self.pattern)
        
        try:
            assert self._sort_by_key(self.fake_dir_fnpattern_res) == self._sort_by_key(res)
        finally:
            self._clean_up_pins()
        

    def test_add_filepattern_subdir_wildcard(self):
        res = self.http_client.add(self.fake_dir, pattern=self.pattern2)
        
        try:
            assert self._sort_by_key(self.fake_dir_fnpattern2_res) == self._sort_by_key(res)
        finally:
            self._clean_up_pins()

    def test_add_recursive(self):
        res = self.http_client.add(self.fake_dir, recursive=True)
        
        try:
            assert self._sort_by_key(self.fake_dir_recursive_res) == self._sort_by_key(res)
        finally:
            self._clean_up_pins()

    def test_add_json(self):
        data = {'Action': 'Open', 'Type': 'PR', 'Name': 'IPFS', 'Pubkey': 7}
        res = self.http_client.add_json(data)
        
        try:
            assert data == self.http_client.get_json(res)

            # have to test the string added to IPFS, deserializing JSON will not
            # test order of keys
            assert '{"Action":"Open","Name":"IPFS","Pubkey":7,"Type":"PR"}' == self.http_client.cat(res).decode('utf-8')
        finally:
            self._clean_up_pins()

    def test_add_get_pyobject(self):
        data = [-1, 3.14, u'Hän€', b'23' ]
        res = self.http_client.add_pyobj(data)
        
        try:
            assert data == self.http_client.get_pyobj(res)
        finally:
            self._clean_up_pins()

    def test_get_file(self):
        self.http_client.add(self.fake_file)
        
        try:
            test_hash = self.fake[0]['Hash']

            self.http_client.get(test_hash)
            assert test_hash in os.listdir(os.getcwd())

            os.remove(test_hash)
            assert test_hash not in os.listdir(os.getcwd())
        finally:
            self._clean_up_pins()

    def test_get_dir(self):
        self.http_client.add(self.fake_dir, recursive=True)
        
        try:
            test_hash = self.fake[8]['Hash']
            
            self.http_client.get(test_hash)
            assert test_hash in os.listdir(os.getcwd())
            
            shutil.rmtree(test_hash)
            assert test_hash not in os.listdir(os.getcwd())
        finally:
            self._clean_up_pins()

    def test_get_path(self):
        self.http_client.add(self.fake_file)
        
        try:
            test_hash = self.fake[8]['Hash'] + '/fsdfgh'
            
            self.http_client.get(test_hash)
            assert 'fsdfgh' in os.listdir(os.getcwd())
            
            os.remove('fsdfgh')
            assert 'fsdfgh' not in os.listdir(os.getcwd())
        finally:
            self._clean_up_pins()

    def test_refs(self):
        self.http_client.add(self.fake_dir, recursive=True)
        
        try:
            refs = self.http_client.refs(self.fake[8]['Hash'])
            assert self._sort_by_key(self.refs_res, "Ref") == self._sort_by_key(refs, "Ref")
        finally:
            self._clean_up_pins()

    def test_cat_single_file_str(self):
        self.http_client.add(self.fake_file)
        
        try:
            content = self.http_client.cat('QmQcCtMgLVwvMQGu6mvsRYLjwqrZJcYtH4mboM9urWW9vX')
            assert content == b"dsadsad\n"
        finally:
            self._clean_up_pins()

    def test_cat_file_block(self):
        self.http_client.add(self.fake_file)

        content = b"dsadsad\n"
        try:
            for offset in range(len(content)):
                for length in range(len(content)):
                    block = self.http_client.cat('QmQcCtMgLVwvMQGu6mvsRYLjwqrZJcYtH4mboM9urWW9vX', offset=offset, length=length)
                    assert block == content[offset:offset+length]
        finally:
            self._clean_up_pins()


@skipIfOffline()
class IpfsHttpClientLogTest(unittest.TestCase):

    def setUp(self):
        self.http_client = ipfshttpclient.Client()

    def test_log_ls_level(self):
        """
        Unfortunately there is no way of knowing the logging levels prior
        to this test. This makes it impossible to guarantee that the logging
        levels are the same as before the test was run.
        """
        # Retrieves the list of logging subsystems for a running daemon.
        resp_ls = self.http_client.log_ls()
        # The response should be a dictionary with only one key ('Strings').
        self.assertTrue('Strings' in resp_ls)

        # Sets the logging level to 'error' for the first subsystem found.
        sub = resp_ls['Strings'][0]
        resp_level = self.http_client.log_level(sub, 'error')
        self.assertEqual(resp_level['Message'],
                         "Changed log level of \'%s\' to 'error'\n" % sub)

    def test_log_tail(self):
        # Gets the response object.
        tail = self.http_client.log_tail()

        # The log should have been parsed into a dictionary object with
        # various keys depending on the event that occured.
        self.assertIs(type(next(tail)), dict)


@skipIfOffline()
class IpfsHttpClientPinTest(unittest.TestCase):
    def setUp(self):
        self.http_client = ipfshttpclient.Client()
        
        # Add resources to be pinned.
        self.resource = self.http_client.add_str('Mary had a little lamb')
        resp_add = self.http_client.add('test/functional/fake_dir', recursive=True)
        self.fake_dir_hashes = [el['Hash'] for el in resp_add if 'Hash' in el]
        for resp in resp_add:
            if resp["Name"] == "fake_dir":
                self.fake_dir_hash = resp["Hash"]
            elif resp["Name"] == "fake_dir/test2":
                self.fake_dir_test2_hash = resp["Hash"]

    def test_pin_ls_add_rm_single(self):
        # Get pinned objects at start.
        pins_begin = self.http_client.pin_ls()['Keys']

        # Unpin the resource if already pinned.
        if self.resource in pins_begin.keys():
            self.http_client.pin_rm(self.resource)

        # No matter what, the resource should not be pinned at this point.
        self.assertNotIn(self.resource, self.http_client.pin_ls()['Keys'])

        for option in [True, False]:
            # Pin the resource.
            resp_add = self.http_client.pin_add(self.resource, recursive=option)
            pins_afer_add = self.http_client.pin_ls()['Keys']
            self.assertEqual(resp_add['Pins'], [self.resource])
            self.assertTrue(self.resource in pins_afer_add)
            self.assertEqual(pins_afer_add[self.resource]['Type'] == 'recursive',
                             option)

            # Unpin the resource.
            resp_rm = self.http_client.pin_rm(self.resource)
            pins_afer_rm = self.http_client.pin_ls()['Keys']
            self.assertEqual(resp_rm['Pins'], [self.resource])
            self.assertFalse(self.resource in pins_afer_rm)

        # Get pinned objects at end.
        pins_end = self.http_client.pin_ls()['Keys']

        # Compare pinned items from start to finish of test.
        self.assertFalse(self.resource in pins_end.keys())

    def test_pin_ls_add_rm_directory(self):
        # Remove fake_dir if it had previously been pinned.
        if self.fake_dir_hash in self.http_client.pin_ls(type="recursive")['Keys'].keys():
            self.http_client.pin_rm(self.fake_dir_hash)

        # Make sure I removed it
        assert self.fake_dir_hash not in self.http_client.pin_ls()['Keys'].keys()

        # Add 'fake_dir' recursively.
        self.http_client.pin_add(self.fake_dir_hash)

        # Make sure all appear on the list of pinned objects.
        pins_after_add = self.http_client.pin_ls()['Keys'].keys()
        for el in self.fake_dir_hashes:
            assert el in pins_after_add

        # Clean up.
        self.http_client.pin_rm(self.fake_dir_hash)
        pins_end = self.http_client.pin_ls(type="recursive")['Keys'].keys()
        assert self.fake_dir_hash not in pins_end
    
    def test_pin_add_update_verify_rm(self):
        # Get pinned objects at start.
        pins_begin = self.http_client.pin_ls(type="recursive")['Keys'].keys()
        
        # Remove fake_dir and demo resource if it had previously been pinned.
        if self.fake_dir_hash in pins_begin:
            self.http_client.pin_rm(self.fake_dir_hash)
        if self.fake_dir_test2_hash in pins_begin:
            self.http_client.pin_rm(self.fake_dir_test2_hash)
        
        # Ensure that none of the above are pinned anymore.
        pins_after_rm = self.http_client.pin_ls(type="recursive")['Keys'].keys()
        assert self.fake_dir_hash       not in pins_after_rm
        assert self.fake_dir_test2_hash not in pins_after_rm
        
        # Add pin for sub-directory
        self.http_client.pin_add(self.fake_dir_test2_hash)
        
        # Replace it by pin for the entire fake dir
        self.http_client.pin_update(self.fake_dir_test2_hash, self.fake_dir_hash)
        
        # Ensure that the sub-directory is not pinned directly anymore
        pins_after_update = self.http_client.pin_ls(type="recursive")["Keys"].keys()
        assert self.fake_dir_test2_hash not in pins_after_update
        assert self.fake_dir_hash           in pins_after_update
        
        # Now add a pin to the sub-directory from the parent directory
        self.http_client.pin_update(self.fake_dir_hash, self.fake_dir_test2_hash, unpin=False)
        
        # Check integrity of all directory content hashes and whether all
        # directory contents have been processed in doing this
        hashes = []
        for result in self.http_client.pin_verify(self.fake_dir_hash, verbose=True):
            assert result["Ok"]
            hashes.append(result["Cid"])
        assert self.fake_dir_hash in hashes
        
        # Ensure that both directories are now recursively pinned
        pins_after_update2 = self.http_client.pin_ls(type="recursive")["Keys"].keys()
        assert self.fake_dir_test2_hash in pins_after_update2
        assert self.fake_dir_hash       in pins_after_update2
        
        # Clean up
        self.http_client.pin_rm(self.fake_dir_hash, self.fake_dir_test2_hash)
        
        


@skipIfOffline()
class IpfsHttpClientMFSTest(unittest.TestCase):

    test_files = {
        'test_file1': {
            u'Name': u'fake_dir/popoiopiu',
            u'Stat': {u'Type': 'file',
                      u'Hash': 'QmUvobKqcCE56brA8pGTRRRsGy2SsDEKSxFLZkBQFv7Vvv',
                      u'Blocks': 1,
                      u'CumulativeSize': 73,
                      u'Size': 15}
        }
    }

    test_directory_path = '/test_dir'

    def setUp(self):
        self.http_client = ipfshttpclient.Client()
        self._olddir = os.getcwd()
        os.chdir(HERE)

    def tearDown(self):
        os.chdir(self._olddir)

    def test_file_write_stat_read_delete(self):
        for filename, desc in self.test_files.items():
            filepath = "/" + filename

            # Create target file
            self.http_client.files_write(filepath, desc[u'Name'], create=True)

            # Verify stat information of file
            stat = self.http_client.files_stat(filepath)
            self.assertEqual(sorted(desc[u'Stat'].items()),
                             sorted(stat.items()))

            # Read back (and compare file contents)
            with open(desc[u'Name'], 'rb') as file:
                content = self.http_client.files_read(filepath)
                self.assertEqual(content, file.read())

            # Remove file
            self.http_client.files_rm(filepath)

    def test_dir_make_fill_list_delete(self):
        self.http_client.files_mkdir(self.test_directory_path)
        for filename, desc in self.test_files.items():
            # Create target file in directory
            self.http_client.files_write(
                self.test_directory_path + "/" + filename,
                desc[u'Name'], create=True
            )

        # Verify directory contents
        contents = self.http_client.files_ls(self.test_directory_path)[u'Entries']
        filenames1 = list(map(lambda d: d[u'Name'], contents))
        filenames2 = list(self.test_files.keys())
        self.assertEqual(filenames1, filenames2)

        # Remove directory
        self.http_client.files_rm(self.test_directory_path, recursive=True)

        with self.assertRaises(ipfshttpclient.exceptions.Error):
            self.http_client.files_stat(self.test_directory_path)


skipIfOffline()
class TestBlockFunctions(unittest.TestCase):
    def setUp(self):
        self.http_client = ipfshttpclient.Client()
        self.multihash = 'QmYA2fn8cMbVWo4v95RwcwJVyQsNtnEwHerfWR8UNtEwoE'
        self.content_size = 248

    def test_block_stat(self):
        expected_keys = ['Key', 'Size']
        res = self.http_client.block_stat(self.multihash)
        for key in expected_keys:
            self.assertTrue(key in res)

    def test_block_get(self):
        self.assertEqual(len(self.http_client.block_get(self.multihash)), self.content_size)

    def test_block_put(self):
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                            "functional", "fake_dir", "fsdfgh")
        expected_block_multihash = 'QmPevo2B1pwvDyuZyJbWVfhwkaGPee3f1kX36wFmqx1yna'
        expected_keys = ['Key', 'Size']
        res = self.http_client.block_put(path)
        for key in expected_keys:
            self.assertTrue(key in res)
        self.assertEqual(res['Key'], expected_block_multihash)


@skipIfOffline()
class IpfsHttpClientRepoTest(unittest.TestCase):

    def setUp(self):
        self.http_client = ipfshttpclient.Client()

    def test_repo_stat(self):
        # Verify that the correct key-value pairs are returned
        stat = self.http_client.repo_stat()
        self.assertEqual(sorted(stat.keys()), [u'NumObjects', u'RepoPath', u'RepoSize',
                                               u'StorageMax', u'Version'])

    def test_repo_gc(self):
        # Add and unpin an object to be garbage collected
        garbage = self.http_client.add_str('Test String')
        self.http_client.pin_rm(garbage)

        # Collect the garbage object with object count before and after
        orig_objs = self.http_client.repo_stat()['NumObjects']
        gc = self.http_client.repo_gc()
        cur_objs = self.http_client.repo_stat()['NumObjects']

        # Verify the garbage object was collected
        self.assertGreater(orig_objs, cur_objs)
        keys = [el['Key']['/'] for el in gc]
        self.assertTrue(garbage in keys)


@skipIfOffline()
class IpfsHttpClientKeyTest(unittest.TestCase):
    def setUp(self):
        self.http_client = ipfshttpclient.Client()

    def test_key_add_list_rename_rm(self):
        # Remove keys if they already exist
        key_list = list(map(lambda k: k["Name"], self.http_client.key_list()["Keys"]))
        if "ipfshttpclient-test-rsa" in key_list:
            self.http_client.key_rm("ipfshttpclient-test-rsa")
        if "ipfshttpclient-test-ed" in key_list:
            self.http_client.key_rm("ipfshttpclient-test-ed")
        
        # Add new RSA and ED25519 key
        key1 = self.http_client.key_gen("ipfshttpclient-test-rsa", "rsa")["Name"]
        key2 = self.http_client.key_gen("ipfshttpclient-test-ed", "ed25519")["Name"]
        
        # Validate the keys exist now
        key_list = list(map(lambda k: k["Name"], self.http_client.key_list()["Keys"]))
        assert key1 in key_list
        assert key2 in key_list
        
        # Rename the EC key
        key2_new = self.http_client.key_rename(key2, "ipfshttpclient-test-ed2")["Now"]
        
        # Validate that the key was successfully renamed
        key_list = list(map(lambda k: k["Name"], self.http_client.key_list()["Keys"]))
        assert key1     in key_list
        assert key2 not in key_list
        assert key2_new in key_list
        
        # Drop both keys with one request
        self.http_client.key_rm(key1, key2_new)
        
        # Validate that the keys are gone again
        key_list = list(map(lambda k: k["Name"], self.http_client.key_list()["Keys"]))
        assert key1     not in key_list
        assert key2_new not in key_list


@skipIfOffline()
class IpfsHttpClientObjectTest(unittest.TestCase):

    def setUp(self):
        self.http_client = ipfshttpclient.Client()
        self._olddir = os.getcwd()
        os.chdir(HERE)
        # Add a resource to get the stats for.
        self.resource = self.http_client.add_str('Mary had a little lamb')

    def tearDown(self):
        os.chdir(self._olddir)

    def test_object_new(self):
        expected_keys = ['Hash']
        res = self.http_client.object_new()
        for key in expected_keys:
            self.assertTrue(key in res)

    def test_object_stat(self):
        expected = ['Hash', 'CumulativeSize', 'DataSize',
                    'NumLinks', 'LinksSize', 'BlockSize']
        resp_stat = self.http_client.object_stat(self.resource)
        for key in expected:
            self.assertTrue(key in resp_stat)

    def test_object_put_get(self):
        # Set paths to test json files
        path_no_links = os.path.join(os.path.dirname(__file__),
                                     "fake_json", "no_links.json")
        path_links = os.path.join(os.path.dirname(__file__),
                                  "fake_json", "links.json")

        # Put the json objects on the DAG
        no_links = self.http_client.object_put(path_no_links)
        links = self.http_client.object_put(path_links)

        # Verify the correct content was put
        self.assertEqual(no_links['Hash'], 'QmXg9Pp2ytZ14xgmQjYEiHjVjMFXzCVVEcRTWJBmLgR39V')
        self.assertEqual(links['Hash'], 'QmZZmY4KCu9r3e7M2Pcn46Fc5qbn6NpzaAGaYb22kbfTqm')

        # Get the objects from the DAG
        get_no_links = self.http_client.object_get('QmXg9Pp2ytZ14xgmQjYEiHjVjMFXzCVVEcRTWJBmLgR39V')
        get_links = self.http_client.object_get('QmZZmY4KCu9r3e7M2Pcn46Fc5qbn6NpzaAGaYb22kbfTqm')

        # Verify the objects we put have been gotten
        self.assertEqual(get_no_links['Data'], 'abc')
        self.assertEqual(get_links['Data'], 'another')
        self.assertEqual(get_links['Links'][0]['Name'], 'some link')

    def test_object_links(self):
        # Set paths to test json files
        path_links = os.path.join(os.path.dirname(__file__),
                                  "fake_json", "links.json")

        # Put json object on the DAG and get its links
        self.http_client.object_put(path_links)
        links = self.http_client.object_links('QmZZmY4KCu9r3e7M2Pcn46Fc5qbn6NpzaAGaYb22kbfTqm')

        # Verify the correct link has been gotten
        self.assertEqual(links['Links'][0]['Hash'], 'QmXg9Pp2ytZ14xgmQjYEiHjVjMFXzCVVEcRTWJBmLgR39V')

    def test_object_data(self):
        # Set paths to test json files
        path_links = os.path.join(os.path.dirname(__file__),
                                  "fake_json", "links.json")

        # Put json objects on the DAG and get its data
        self.http_client.object_put(path_links)
        data = self.http_client.object_data('QmZZmY4KCu9r3e7M2Pcn46Fc5qbn6NpzaAGaYb22kbfTqm')

        # Verify the correct bytes have been gotten
        self.assertEqual(data, b'another')

    def test_object_patch_append_data(self):
        """Warning, this test depends on the contents of
            test/functional/fake_dir/fsdfgh
        """
        result = self.http_client.object_patch_append_data(
                'QmdfTbBqBPQ7VNxZEYEj14VmRuZBkqFbiwReogJgS1zR1n', 'fake_dir/fsdfgh')
        self.assertEqual(result,
                {'Hash': 'QmcUsyoGVxWoQgYKgmLaDBGm8J3eHWfchMh3oDUD5FrrtN'})

    def test_object_patch_add_link(self):
        """Warning, this test depends on the contents of
            test/functional/fake_dir/fsdfgh
        """
        result = self.http_client.object_patch_add_link(
                'QmdfTbBqBPQ7VNxZEYEj14VmRuZBkqFbiwReogJgS1zR1n', 'self',
                'QmdfTbBqBPQ7VNxZEYEj14VmRuZBkqFbiwReogJgS1zR1n')
        self.assertEqual(result,
                {'Hash': 'QmbWSr7YXBLcF23VVb7yPvUuogUPn46GD7gXftXC6mmsNM'})

    def test_object_patch_rm_link(self):
        """Warning, this test depends on the contents of
            test/functional/fake_dir/fsdfgh
        """
        result = self.http_client.object_patch_rm_link(
                'QmbWSr7YXBLcF23VVb7yPvUuogUPn46GD7gXftXC6mmsNM', 'self')
        self.assertEqual(result,
                {'Hash': 'QmdfTbBqBPQ7VNxZEYEj14VmRuZBkqFbiwReogJgS1zR1n'})

    def test_object_patch_set_data(self):
        """Warning, this test depends on the contents of
            test/functional/fake_dir/popoiopiu
        """
        result = self.http_client.object_patch_set_data(
                'QmdfTbBqBPQ7VNxZEYEj14VmRuZBkqFbiwReogJgS1zR1n', 'fake_dir/popoiopiu')
        self.assertEqual(result,
                {'Hash': 'QmV4QR7MCBj5VTi6ddHmXPyjWGzbaKEtX2mx7axA5PA13G'})

@skipIfOffline()
class IpfsHttpClientBitswapTest(unittest.TestCase):

    def setUp(self):
        self.http_client = ipfshttpclient.Client()

    def test_bitswap_wantlist(self):
        result = self.http_client.bitswap_wantlist(peer='QmdkJZUWnVkEc6yfptVu4LWY8nHkEnGwsxqQ233QSGj8UP')
        self.assertTrue(result and type(result) is dict and 'Keys' in result)

    def test_bitswap_stat(self):
        result = self.http_client.bitswap_stat()
        self.assertTrue(result and type(result) is dict and 'Wantlist' in result)

    def test_bitswap_unwant(self):
        """
        Cannot ensure what is present in the wantlist prior to execution, so just ensure
        something comes back.
        """

        result = self.http_client.bitswap_unwant(key='QmZTR5bcpQD7cFgTorqxZDYaew1Wqgfbd2ud9QqGPAkK2V')
        self.assertTrue(result is not None)

@skipIfOffline()
class IpfsHttpClientPubSubTest(unittest.TestCase):

    def setUp(self):
        self.http_client = ipfshttpclient.Client()

    def createTestChannel(self):
        """
        Creates a unique topic for testing purposes
        """
        return "{}.testing".format(uuid.uuid4())

    def test_pubsub_pub_sub(self):
        """
        We test both publishing and subscribing at
        the same time because we cannot verify that
        something has been properly published unless
        we subscribe to that channel and receive it.
        Likewise, we cannot accurately test a subscription 
        without publishing something on the topic we are subscribed
        to.
        """
        # the topic that will be published/subscribed to
        topic = self.createTestChannel()
        # the message that will be published
        message = 'hello'

        expected_data = 'aGVsbG8='	
        expected_topicIDs = [topic]


        # get the subscription stream
        with self.http_client.pubsub_sub(topic) as sub:

            # make sure something was actually returned from the subscription
            assert sub is not None

            # publish a message to topic
            self.http_client.pubsub_pub(topic, message)

            # get the message
            sub_data = sub.read_message()

            # assert that the returned dict has the following keys
            assert 'data' in sub_data
            assert 'topicIDs' in sub_data

            assert sub_data['data'] == expected_data
            assert sub_data['topicIDs'] == expected_topicIDs

    def test_pubsub_ls(self):
        """
        Testing the ls, assumes we are able
        to at least subscribe to a topic
        """
        topic = self.createTestChannel()
        expected_return = { 'Strings': [topic] }

        # subscribe to the topic testing
        sub = self.http_client.pubsub_sub(topic)

        channels = None
        try:
            # grab the channels we're subscribed to
            channels = self.http_client.pubsub_ls()
        finally:
            sub.close()

        assert channels == expected_return

    def test_pubsub_peers(self):
        """
        Not sure how to test this since it fully depends
        on who we're connected to. We may not even have
        any peers
        """
        peers = self.http_client.pubsub_peers()

        expected_return = {
                'Strings': []
                }

        # make sure the Strings key is in the map thats returned
        assert 'Strings' in peers

        # ensure the value of 'Strings' is a list.
        # The list may or may not be empty.
        assert isinstance(peers['Strings'], list)


# Run test for `.shutdown()` only as the last test in CI environments – it would be to annoying
# during normal testing
@skipIfOffline()
@skipUnlessCI()
@pytest.mark.last
class IpfsHttpClientShutdownTest(unittest.TestCase):
    def setUp(self):
        self.http_client = ipfshttpclient.Client()
        self.pid = int(os.environ["PY_IPFS_HTTP_CLIENT_TEST_DAEMON_PID"])
    
    @staticmethod
    def _pid_exists(pid):
        """
        Check whether pid exists in the current process table

        Source: https://stackoverflow.com/a/23409343/277882
        """
        if os.name == 'posix':
            import errno
            if pid < 0:
                return False
            try:
                os.kill(pid, 0)
            except OSError as e:
                return e.errno == errno.EPERM
            else:
                return True
        else:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            HANDLE = ctypes.c_void_p
            DWORD = ctypes.c_ulong
            LPDWORD = ctypes.POINTER(DWORD)
            class ExitCodeProcess(ctypes.Structure):
                _fields_ = [ ('hProcess', HANDLE),
                    ('lpExitCode', LPDWORD)]

            SYNCHRONIZE = 0x100000
            process = kernel32.OpenProcess(SYNCHRONIZE, 0, pid)
            if not process:
                return False

            ec = ExitCodeProcess()
            out = kernel32.GetExitCodeProcess(process, ctypes.byref(ec))
            if not out:
                err = kernel32.GetLastError()
                if kernel32.GetLastError() == 5:
                    # Access is denied.
                    logging.warning("Access is denied to get pid info.")
                kernel32.CloseHandle(process)
                return False
            elif bool(ec.lpExitCode):
                # There is an exit code, it quit
                kernel32.CloseHandle(process)
                return False
            # No exit code, it's running.
            kernel32.CloseHandle(process)
            return True
    
    def _is_ipfs_running(self):
        return self._pid_exists(self.pid)
    
    
    def test_daemon_shutdown(self):
        # Daemon should still be running at this point
        assert self._is_ipfs_running()
        
        # Send stop request
        self.http_client.shutdown()
        
        # Wait for daemon process to disappear
        for _ in range(10000):
            if not self._is_ipfs_running():
                break
            time.sleep(0.001)
        
        # Daemon should not be running anymore
        assert not self._is_ipfs_running()
        


if __name__ == "__main__":
    unittest.main()
