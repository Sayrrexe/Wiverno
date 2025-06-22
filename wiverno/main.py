import traceback
import logging

from typing import Callable, Dict, List, Tuple
from wiverno.core.requests import Request
from wiverno.templating.templator import Templator

logger = logging.getLogger(__name__)


class PageNotFound404:
    
    def __call__(self, request):
        templator = Templator(folder="wiverno\\static\\templates")
        return "404 WHAT", templator.render('error_404.html')

class MethodNotAllowed405:
    
    def __call__(self, request):
        templator = Templator(folder="wiverno/static/templates")
        return "405 METHOD NOT ALLOWED", templator.render(
            "error_405.html", content={"method": request.method}
        )


class Wiverno:
    """
    A simple WSGI-compatible web framework.
    """

    def __init__(
        self,
        routes_list: List[Tuple[str, Callable[[Request], Tuple[str, str]]]],
        page_404: Callable[[Request], Tuple[str, str]] = PageNotFound404(),
        debug_mode: bool = True,
        system_template_path: str = "wiverno\\static\\templates",
        page_500: Callable[[Request], Tuple[str, str]] = None
    ):
        """
        Initializes the Wiverno application with a list of routes.

        Args:
            routes_list: List of tuples (path, view-function).
            page_404: Callable to handle 404 errors (optional).
            page_500: Callable to handle 500 errors (optional).
            debug_mode: Enable or disable debug mode (default is True).
            system_template_path: Path to base templates used for error pages.
        """
        self.routes_list: Dict[str, Callable[[Request], Tuple[str, str]]] = dict(routes_list)
        self.page_404: Callable[[Request], Tuple[str, str]] = page_404 
        self.system_templator: str = Templator(folder=system_template_path)
        self.debug: bool = debug_mode
        self.page_500: Callable[[Request], Tuple[str, str]] = page_500


    def __call__(self, 
                 environ: dict, 
                 start_response: Callable[[str, List[Tuple[str, str]]], None]
                 ) -> List[bytes]:
        request = Request(environ)
        try:
            view = self.routes_list.get(request.path, self.page_404)
            status, body = view(request)
        except Exception:
            logger.exception("Unhandled exception in view handler")
            if self.page_500:
                status, body = self.page_500(request)
            else:
                status = "500 INTERNAL SERVER ERROR"
                body = self.system_templator.render('error_500.html', content = {"debug": self.debug, 'traceback': traceback.format_exc()})

        start_response(status, [("Content-Type", "text/html; charset=utf-8")])
        return [body.encode("utf-8")]
