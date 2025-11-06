import traceback
import logging

from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

from wiverno.core.requests import Request
from wiverno.templating.templator import Templator
from wiverno.core.router import Router


logger = logging.getLogger(__name__)


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_TEMPLATE_PATH = BASE_DIR / "static" / "templates"


class PageNotFound404:

    def __call__(self, request):
        templator = Templator(folder=str(DEFAULT_TEMPLATE_PATH))
        return "404 NOT FOUND", templator.render('error_404.html')

class MethodNotAllowed405:

    def __call__(self, request):
        templator = Templator(folder=str(DEFAULT_TEMPLATE_PATH))
        return "405 METHOD NOT ALLOWED", templator.render(
            "error_405.html", content={"method": request.method}
        )
        
class InternalServerError500:

    def __call__(self, request, error_traceback: str = None):
        templator = Templator(folder=str(DEFAULT_TEMPLATE_PATH))
        return "500 INTERNAL SERVER ERROR", templator.render(
            'error_500.html', content = {"traceback": error_traceback})


class Wiverno:
    """
    A simple WSGI-compatible web framework.
    """

    def __init__(
        self,
        routes_list: Optional[List[Tuple[str, Callable[[Request], Tuple[str, str]]]]] = None,
        debug_mode: bool = True,
        system_template_path: str = str(DEFAULT_TEMPLATE_PATH),
        page_404: Callable[[Request], Tuple[str, str]] = PageNotFound404(),
        page_405: Callable[[Request], Tuple[str, str]] = MethodNotAllowed405(),
        page_500: Callable[[Request, Optional[str]], Tuple[str, str]] = InternalServerError500(),
        
    ):
        """
        Initializes the Wiverno application with a list of routes.

        Args:
            routes_list: List of tuples (path, view-function), (optional).
            debug_mode: Enable or disable debug mode (default is True).
            system_template_path: Path to base templates used for error pages.
            page_404: Callable to handle 404 errors (optional).
            page_405: Callable to handle 405 errors (optional).
            page_500: Callable to handle 500 errors (optional).
        """
        self._routes: Dict[str, Dict] = {}
        if routes_list:
            for path, handler in routes_list:
                self._routes[path] = {
                    'handler': handler,
                    'methods': None 
                }
        self.system_templator = Templator(folder=system_template_path)
        self.debug = debug_mode
        self.page_404 = page_404
        self.page_405 = page_405
        self.page_500 = page_500


    def route(self, path: str, methods: Optional[List[str]] = None):
        def decorator(func):
            normalized_path = '/' + path.strip('/')
            if normalized_path != '/':
                normalized_path = normalized_path.rstrip('/')
            
            self._routes[normalized_path] = {
                'handler': func,
                'methods': methods
            }
            return func
        return decorator
    
    def get(self, path: str):
        return self.route(path, methods=['GET'])
    
    def post(self, path: str):
        return self.route(path, methods=['POST'])
    
    def put(self, path: str):
        return self.route(path, methods=['PUT'])
    
    def patch(self, path: str):
        return self.route(path, methods=['PATCH'])
    
    def delete(self, path: str):
        return self.route(path, methods=['DELETE'])
    
    def connect(self, path: str):
        return self.route(path, methods=['CONNECT'])
    
    def head(self, path: str):
        return self.route(path, methods=['HEAD'])
    
    def options(self, path: str):
        return self.route(path, methods=['OPTIONS'])
    
    def trace(self, path: str):
        return self.route(path, methods=['TRACE'])
    
    def include_router(self, router: Router, prefix: str = ''):
        for route_info in router._routes:
            full_path = prefix + route_info['path']
            
            full_path = '/' + full_path.strip('/')
            if full_path != '/':
                full_path = full_path.rstrip('/')
            
            self._routes[full_path] = {
                'handler': route_info['handler'],
                'methods': route_info['methods']
            }
    
    def _match_route(self, request: Request):
        route_info = self._routes.get(request.path)
        
        
        if not route_info:
            return None, None
        
        handler = route_info['handler']
        allowed_methods = route_info['methods']
        
        if allowed_methods is None:
            return handler, True
        
        method_allowed = request.method in allowed_methods
        
        return handler, method_allowed


    def __call__(
        self, 
        environ: dict, 
        start_response: Callable[[str, List[Tuple[str, str]]], None]
        ) -> List[bytes]:
        
        request = Request(environ)
        
        normalized_path = request.path.rstrip('/') if request.path != '/' else request.path
        request.path = normalized_path
        
        try:
            handler, method_allowed = self._match_route(request)
            print(handler, method_allowed)
            
            if handler is None:
                status, body = self.page_404(request)
            
            elif not method_allowed:
                status, body = self.page_405(request)
            else:
                status, body = handler(request)
    
        except Exception:
            logger.exception("Unhandled exception in view handler")
            if self.debug:
                error_traceback = traceback.format_exc()
            else:
                error_traceback = None
            status, body = self.page_500(request, error_traceback)
        
        start_response(status, [("Content-Type", "text/html; charset=utf-8")])
        return [body.encode("utf-8")]
