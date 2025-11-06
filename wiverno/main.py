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
    """
    Default 404 error handler that renders the error_404.html template.
    """

    def __call__(self, request):
        """
        Handles 404 Not Found errors.

        Args:
            request (Request): The incoming request object.

        Returns:
            tuple[str, str]: A tuple of (status, html_body).
        """
        templator = Templator(folder=str(DEFAULT_TEMPLATE_PATH))
        return "404 NOT FOUND", templator.render('error_404.html')

class MethodNotAllowed405:
    """
    Default 405 error handler that renders the error_405.html template.
    """

    def __call__(self, request):
        """
        Handles 405 Method Not Allowed errors.

        Args:
            request (Request): The incoming request object.

        Returns:
            tuple[str, str]: A tuple of (status, html_body).
        """
        templator = Templator(folder=str(DEFAULT_TEMPLATE_PATH))
        return "405 METHOD NOT ALLOWED", templator.render(
            "error_405.html", content={"method": request.method}
        )
        
class InternalServerError500:
    """
    Default 500 error handler that renders the error_500.html template.
    """

    def __call__(self, request, error_traceback: str = None):
        """
        Handles 500 Internal Server Error.

        Args:
            request (Request): The incoming request object.
            error_traceback (str, optional): The traceback string if debug mode is enabled.

        Returns:
            tuple[str, str]: A tuple of (status, html_body).
        """
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
        """
        Decorator to register a route with the application.

        Args:
            path (str): The URL path for the route.
            methods (Optional[List[str]]): Allowed HTTP methods for this route.
                If None, all methods are allowed.

        Returns:
            Callable: The decorator function.
        """
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
        """
        Decorator to register a GET route.

        Args:
            path (str): The URL path for the route.

        Returns:
            Callable: The decorator function.
        """
        return self.route(path, methods=['GET'])
    
    def post(self, path: str):
        """
        Decorator to register a POST route.

        Args:
            path (str): The URL path for the route.

        Returns:
            Callable: The decorator function.
        """
        return self.route(path, methods=['POST'])
    
    def put(self, path: str):
        """
        Decorator to register a PUT route.

        Args:
            path (str): The URL path for the route.

        Returns:
            Callable: The decorator function.
        """
        return self.route(path, methods=['PUT'])
    
    def patch(self, path: str):
        """
        Decorator to register a PATCH route.

        Args:
            path (str): The URL path for the route.

        Returns:
            Callable: The decorator function.
        """
        return self.route(path, methods=['PATCH'])
    
    def delete(self, path: str):
        """
        Decorator to register a DELETE route.

        Args:
            path (str): The URL path for the route.

        Returns:
            Callable: The decorator function.
        """
        return self.route(path, methods=['DELETE'])
    
    def connect(self, path: str):
        """
        Decorator to register a CONNECT route.

        Args:
            path (str): The URL path for the route.

        Returns:
            Callable: The decorator function.
        """
        return self.route(path, methods=['CONNECT'])
    
    def head(self, path: str):
        """
        Decorator to register a HEAD route.

        Args:
            path (str): The URL path for the route.

        Returns:
            Callable: The decorator function.
        """
        return self.route(path, methods=['HEAD'])
    
    def options(self, path: str):
        """
        Decorator to register an OPTIONS route.

        Args:
            path (str): The URL path for the route.

        Returns:
            Callable: The decorator function.
        """
        return self.route(path, methods=['OPTIONS'])
    
    def trace(self, path: str):
        """
        Decorator to register a TRACE route.

        Args:
            path (str): The URL path for the route.

        Returns:
            Callable: The decorator function.
        """
        return self.route(path, methods=['TRACE'])
    
    def include_router(self, router: Router, prefix: str = ''):
        """
        Includes routes from a Router instance into the application.

        Args:
            router (Router): The Router instance containing routes to include.
            prefix (str, optional): URL prefix to prepend to all router paths. Defaults to ''.
        """
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
        """
        Matches the request path and method to a registered route.

        Args:
            request (Request): The incoming request object.

        Returns:
            tuple[Callable | None, bool | None]: A tuple of (handler, method_allowed).
                - handler: The route handler function if found, None otherwise.
                - method_allowed: True if the method is allowed, False if not, None if route not found.
        """
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
        """
        WSGI application entry point.

        Args:
            environ (dict): The WSGI environment dictionary.
            start_response (Callable[[str, List[Tuple[str, str]]], None]):
                WSGI start_response callable.

        Returns:
            List[bytes]: Response body as a list of byte strings.
        """

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
