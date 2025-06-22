from unittest import mock

from wiverno.core.server import RunServer


def dummy_app(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/plain')])
    return [b'OK']


def test_runserver_start():
    server = RunServer(dummy_app, host='127.0.0.1', port=9000)
    with mock.patch('wiverno.core.server.make_server') as ms:
        httpd = mock.MagicMock()
        ms.return_value.__enter__.return_value = httpd
        server.start()
        ms.assert_called_with('127.0.0.1', 9000, dummy_app)
        httpd.serve_forever.assert_called_once()

