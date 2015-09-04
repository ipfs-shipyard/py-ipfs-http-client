import os
import httplib
from urllib import quote
import mimetypes
import uuid
import fnmatch


base = 'http://127.0.0.1:5001/api/v0/add'
from urlparse import urlsplit


def gen_boundary():
    return uuid.uuid4().hex


def recursive_glob(root, pattern='*'):
    results = []
    for base, dirs, files in os.walk(root):
        goodfiles = fnmatch.filter(files, pattern)
        results.extend(os.path.join(base, f) for f in goodfiles)
    return results






def post_multipart(dirname, pattern='*'):
    """
    Post fields and files to an http host as multipart/form-data.
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return the server's response page.
    """
    body, content_type = encode_multipart(dirname, pattern)
    print body

    u = urlsplit(base)
    host = u.netloc
    selector = u.path
   
    h = httplib.HTTP(host)
    h.putrequest('POST', selector + '?stream-channels=true')
    h.putheader('transfer-encoding', 'chunked')
    h.putheader('content-disposition', 'form-data: name="{}"'.format(dirname))
    h.putheader('content-type', content_type)
    h.putheader('content-length', str(len(body)))
    h.putheader('accept-encoding', 'gzip')
    h.endheaders()
    h.send(body)
    errcode, errmsg, headers = h.getreply()
    print '=============================='
    print errcode
    print errmsg
    print headers
    print h.file.read()
    #return h.file.read()


def encode_multipart(dirname, pattern):
    crlf = '\r\n'
    
    boundary = gen_boundary()

    lines = []
    for _fn in os.listdir(dirname):
        fn = os.path.join(dirname, _fn)
        if os.path.isfile(fn):
            lines += encode_multipart_file(dirname, _fn, boundary)
        elif os.path.isdir(fn):
            lines.append('--' + boundary)
            lines += _walk(fn, dirname)

    lines.append('--' + boundary + '--')
    lines.append('')

    body = crlf.join(lines)
    content_type = 'multipart/form-data; boundary={}'.format(boundary)
    
    return body, content_type


def _walk(dirname, parent):
    lines = []
    
    ls = os.listdir(dirname)
    files = filter(lambda p: os.path.isfile(os.path.join(dirname, p)), ls)
    dirs  = filter(lambda p: os.path.isdir(os.path.join(dirname, p)), ls)

    body, end = encode_multipart_dir(dirname, files)

    lines += body
    for d in dirs:
        lines += _walk(os.path.join(dirname,d), dirname)
    lines += end

    return lines


def encode_multipart_file(dirname, fn, boundary):
    filename = os.path.join(dirname, fn)
    lines = []
    lines.append('--' + boundary)
    lines.append('Content-Disposition: file; filename="{}"'.format(quote(filename, safe='')))
    lines.append('Content-Type: {}'.format(get_content_type(fn)))
    lines.append('')
    with open(filename, 'rb') as f:
        lines.append(f.read())
    return lines


def encode_multipart_dir(dirname, filenames):
    boundary = gen_boundary()
    lines = []
    lines.append('Content-Disposition: form-data; name="file"; filename="{}"'.format(quote(dirname, safe='')))
    lines.append('Content-Type: multipart/mixed; boundary={}'.format(boundary))
    lines.append('')
    lines.append('')
    for fn in filenames:
        lines += encode_multipart_file(dirname, fn, boundary)
    lines.append('')
    
    end = ['', '--' + boundary + '--', '']
    return lines, end 


def get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'


if __name__ == "__main__":
    
    test = """
-2186ef15d8f2c4f100af72d6d345afe36a4d17ef11264ec5b8ec4436447f
Content-Disposition: form-data; name="file"; filename="test"
Content-Type: multipart/mixed; boundary=acdb172fe12f25e8ffae9981ce6f4580abdefb0cae3ceebe464d802866be


9c
--acdb172fe12f25e8ffae9981ce6f4580abdefb0cae3ceebe464d802866be
Content-Disposition: file; filename="test%2Fbar"
Content-Type: application/octet-stream


4
bar

dc

--acdb172fe12f25e8ffae9981ce6f4580abdefb0cae3ceebe464d802866be
Content-Disposition: file; filename="test%2Fbaz"
Content-Type: multipart/mixed; boundary=2799ac77a72ef7b8a0281945806b9f9a28f7681145aa8e91b052d599b2dd


a0
--2799ac77a72ef7b8a0281945806b9f9a28f7681145aa8e91b052d599b2dd
Content-Type: application/octet-stream
Content-Disposition: file; filename="test%2Fbaz%2Fb"


4
bar

a2

--2799ac77a72ef7b8a0281945806b9f9a28f7681145aa8e91b052d599b2dd
Content-Disposition: file; filename="test%2Fbaz%2Ff"
Content-Type: application/octet-stream


4
foo

44

--2799ac77a72ef7b8a0281945806b9f9a28f7681145aa8e91b052d599b2dd--

9e

--acdb172fe12f25e8ffae9981ce6f4580abdefb0cae3ceebe464d802866be
Content-Disposition: file; filename="test%2Ffoo"
Content-Type: application/octet-stream


4
foo

44

--acdb172fe12f25e8ffae9981ce6f4580abdefb0cae3ceebe464d802866be--

44

--2186ef15d8f2c4f100af72d6d345afe36a4d17ef11264ec5b8ec4436447f--

"""
    u = urlsplit(base)
    host = u.netloc
    selector = u.path
   
    h = httplib.HTTP(host)
    h.putrequest('POST', selector + '?stream-channels=true')
    h.putheader('transfer-encoding', 'chunked')
    h.putheader('content-disposition', 'form-data: name="{}"'.format('test'))
    h.putheader('content-type', 'multipart/form-data; boundary=2186ef15d8f2c4f100af72d6d345afe36a4d17ef11264ec5b8ec4436447f')
    h.putheader('accept-encoding', 'gzip')
    h.putheader('user-agent', 'poopoo wizard')
    h.endheaders()
    h.send(test)
    errcode, errmsg, headers = h.getreply()
    print '=============================='
    print errcode
    print errmsg
    print headers
    print h.file.read()
