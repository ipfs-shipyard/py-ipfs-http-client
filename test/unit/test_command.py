"""Test commands.py.

Classes:
TestCommands -- test the functionality of the commands

Functions:
cmd_simple -- defines an endpoint for simple commands
cmd_with_arg -- defines an endpoint for commands that have arguments
cmd_with_file -- defines an endpoint for commands that handle files
"""

import unittest
import json
import six
from six.moves.urllib import parse as urlparse
from six.moves import cStringIO as StringIO
import requests
from httmock import urlmatch, HTTMock

import ipfsApi.commands
import ipfsApi.exceptions

@urlmatch(netloc='localhost:5001', path=r'.*/simple')
def cmd_simple(url, request):
    """Defines an endpoint for simple commands.

    This endpoint will listen at http://localhost:5001/*/simple for incoming
    requests and will always respond with a 200 status code and a Message of
    "okay".

    Keyword arguments:
    url -- the url of the incoming request
    request -- the request that is being responded to
    """
    return {
        'status_code': 200,
        'content': json.dumps({
            'Message': 'okay',
        }).encode('utf-8'),
    }


@urlmatch(netloc='localhost:5001', path=r'.*/arg')
def cmd_with_arg(url, request):
    """Defines an endpoint for commands that have arguments.

    This endpoint will listen at http://localhost:5001/*/arg for incoming
    requests and will always respond with a 200 status code, a Message of
    "okay", and a list of Args.

    Keyword arguments:
    url -- the url of the incoming request
    request -- the request that is being responded to
    """
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
    """Defines an endpoint for commands that handle files.

    This endpoint will listen at http://localhost:5001/*/file for incoming
    requests and will always respond with a 200 status code, a Message of
    "okay", and a file.

    Keyword arguments:
    url -- the url of the incoming request
    request -- the request that is being responded to
    """
    # request.body is a byte generator
    body = []
    for b in request.body:
        try:
            body.append(b.decode('utf-8'))
        except AttributeError:
            body.append(b)
    body = ''.join(body)

    return {
        'status_code': 200,
        'content': json.dumps({
            'Message': 'okay',
            'Body': body,
        }).encode('utf-8'),
    }


class TestCommands(unittest.TestCase):
    """Test the functionality of the commands.py classes.

    Public methods:
    setUp -- create an HTTP client
    test_simple_command -- test the Command class
    test_arg_command_no_args -- test the ArgCommand class without a specific
                                number of arguments
    test_arg_command_with_args -- test the ArgCommand with a specific number
                                of arguments
    test_arg_command_wrong_num_args -- test that the ArgCommand class fails
                                        when given the wrong number of
                                        arguments
    test_file_command_fd -- TODO 
    """

    def setUp(self):
        """Prepare tests."""
        self._client = ipfsApi.http.HTTPClient(
            'localhost',
            5001,
            'api/v0',
            'json')

    def test_simple_command(self):
        """Test the Command class."""
        with HTTMock(cmd_simple):
            cmd = ipfsApi.commands.Command('/simple')
            res = cmd.request(self._client)
            self.assertEquals(res['Message'], 'okay')

    def test_arg_command_no_args(self):
        """Test the ArgCommand class without a specific number of arguments."""
        with HTTMock(cmd_with_arg):
            # test without arguments
            cmd = ipfsApi.commands.ArgCommand('/arg')
            res = cmd.request(self._client, 'arg1')
            self.assertEquals(res['Arg'][0], 'arg1')

    def test_arg_command_with_args(self):
        """Test the ArgCommand with a specific number of arguments."""
        with HTTMock(cmd_with_arg):
            #test with arguments
            cmd = ipfsApi.commands.ArgCommand('/arg', 2)
            res = cmd.request(self._client, 'arg1', 'first')
            self.assertEquals(res['Arg'], ['arg1', 'first'])

    def test_arg_command_wrong_num_args(self):
        """Test that the ArgCommand class fails when given the wrong number of arguments."""
        with HTTMock(cmd_with_arg):
            #test with wrong number of arguments
            cmd = ipfsApi.commands.ArgCommand('/arg', 2)
            self.assertRaises(ipfsApi.exceptions.InvalidArguments, cmd.request, self._client, 'arg1')

    def test_file_command_fd(self):
        """Test a simple FileCommand."""
        data = 'content\ngoes\nhere'
        fd = StringIO(data)
        with HTTMock(cmd_with_file):
            cmd = ipfsApi.commands.FileCommand('/file')
            res = cmd.request(self._client, (), fd)
            self.assertTrue(data in res['Body'])
