import unittest
import json
from six.moves.urllib import parse as urlparse
from six.moves import cStringIO as StringIO
import requests
from httmock import urlmatch, HTTMock

import ipfsApi.commands
import ipfsApi.exceptions


@urlmatch(netloc='localhost:5001', path=r'.*/simple')
def cmd_simple(url, request):
    return {
        'status_code': 200,
        'content': json.dumps({
            'Message': 'okay',
        }).encode('utf-8'),
    }


@urlmatch(netloc='localhost:5001', path=r'.*/arg')
def cmd_with_arg(url, request):
    qs = urlparse.parse_qs(url.query)
    return {
        'status_code': 200,
        'content': json.dumps({
            'Message': 'okay',
            'Arg': qs['arg'],
        }).encode('utf-8'),
    }


@urlmatch(netloc='localhost:5001', path=r'.*/file')
def cmd_with_file(url, request):
    return {
        'status_code': 200,
        'content': json.dumps({
            'Message': 'okay',
            'Body': request.body.decode('utf-8'),
        }).encode('utf-8'),
    }


class TestCommands(unittest.TestCase):
    def setUp(self):
        self._client = ipfsApi.http.HTTPClient(
            'localhost',
            5001,
            'api/v0',
            'json')

    @ipfsApi.commands.Command('/simple')
    def simple(req, **kwargs):
        return req(**kwargs)

    def test_simple_command(self):
        with HTTMock(cmd_simple):
            res = self.simple()
            self.assertEquals(res['Message'], 'okay')
    
    @ipfsApi.commands.ArgCommand('/arg')
    def with_arg(req, *args, **kwargs):
        return req(*args, **kwargs)

    def test_arg_command(self):
        with HTTMock(cmd_with_arg):
            res = self.with_arg('arg1')
            self.assertEquals(res['Arg'][0], 'arg1')
    
    @ipfsApi.commands.FileCommand('/file')
    def with_file(req, files, **kwargs):
        return req(files, **kwargs)

    def test_file_command_fd(self):
        data = 'content\ngoes\nhere'
        fd = StringIO(data)
        with HTTMock(cmd_with_file):
            res = self.with_file(fd)
            self.assertTrue(data in res['Body'])
