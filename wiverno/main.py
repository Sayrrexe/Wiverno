from typing import Callable, Dict, Any
from wiverno.requests import PostRequest, GetRequest


class PageNotFound404:
    def __call__(self, request=None) -> tuple[str, str]:
        return "404 WHAT", "Page not found"


class Wiverno:
    """
    A simple WSGI-compatible web framework.
    
    Args:
        routes_list (dict): A mapping of paths to view callables.
    """

    def __init__(self, routes_list: Dict[str, Callable[[dict], tuple[str, str]]]):
        self.routes_list = routes_list

    def __call__(self, environ: dict, start_response: Callable) -> list[bytes]:
        print("Wiverno is running...")
        path: str = environ.get('PATH_INFO', '/')

        if not path.endswith('/'):
            path += '/'

        request: Dict[str, Any] = {'method': environ.get('REQUEST_METHOD', 'GET')}

        if request['method'] == 'POST':
            request['data'] = PostRequest().get_request_params(environ)
        elif request['method'] == 'GET':
            request['data'] = GetRequest().get_request_params(environ)

        
        try:
            view = self.routes_list.get(path, PageNotFound404())
            code, body = view(request)
            if not body:
                body = "<h1>Page not found</h1>"
                code = "404 NOT FOUND"
        except Exception as e:
            print(f"Error: {e}")
            body = "<h1>Internal Server Error</h1>"
            code = "500 INTERNAL SERVER ERROR" 
            
        start_response(code, [('Content-Type', 'text/html')])
        return [body.encode('utf-8')]
