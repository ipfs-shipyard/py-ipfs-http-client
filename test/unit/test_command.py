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
        self.client = ipfsApi.http.HTTPClient(
            'localhost',
            5001,
            'api/v0',
            'json')

    def test_simple_command(self):
        with HTTMock(cmd_simple):
            cmd = ipfsApi.commands.Command('/simple')
            res = cmd.prepare(self.client)()
            self.assertEquals(res['Message'], 'okay')

    def test_arg_command(self):
        with HTTMock(cmd_with_arg):
            cmd = ipfsApi.commands.ArgCommand('/arg')
            res = cmd.prepare(self.client)('arg1')
            self.assertEquals(res['Arg'][0], 'arg1')

    def test_file_command_fd(self):
        data = 'content\ngoes\nhere'
        fd = StringIO(data)
        with HTTMock(cmd_with_file):
            cmd = ipfsApi.commands.FileCommand('/file')
            res = cmd.prepare(self.client)(fd)
            self.assertTrue( data in res['Body'] )
