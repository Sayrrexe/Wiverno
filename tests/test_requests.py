import io
from wiverno.core.requests import Request

def test_get_request_parsing():
    environ = {
        'REQUEST_METHOD': 'GET',
        'PATH_INFO': '/hello/',
        'QUERY_STRING': 'name=Wiverno',
        'wsgi.input': io.BytesIO(b''),
    }
    req = Request(environ)
    assert req.method == 'GET'
    assert req.path == '/hello/'
    assert req.query_params == {'name': 'Wiverno'}

