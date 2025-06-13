from typing import Callable, Dict, Any
from wiverno.requests import PostRequest, GetRequest


class PageNotFound404:
    def __call__(self) -> tuple[str, str]:
        return "404 WHAT", "Page not found"


class Wiverno:
    """
    A simple WSGI-compatible web framework.
    
    Args:
        routes_list (dict): A mapping of paths to view callables.
    """

    def __init__(self, routes_list: Dict[str, Callable[[], tuple[str, str]]]):
        self.routes_list = routes_list

    def __call__(self, environ: dict, start_response: Callable) -> list[bytes]:
        path: str = environ.get('PATH_INFO', '/')

        if not path.endswith('/'):
            path += '/'

        request: Dict[str, Any] = {'method': environ.get('REQUEST_METHOD', 'GET')}

        if request['method'] == 'POST':
            request['data'] = PostRequest().get_request_params(environ)
            print(f"POST Request data: {request['data']}")
        elif request['method'] == 'GET':
            request['data'] = GetRequest().get_request_params(environ)
            print(f"GET Request data: {request['data']}")

        view = self.routes_list.get(path, PageNotFound404())
        code, body = view()

        start_response(code, [('Content-Type', 'text/html')])
        return [body.encode('utf-8')]
