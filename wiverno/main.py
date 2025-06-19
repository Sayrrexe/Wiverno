import traceback
import logging

from typing import Callable, Dict, List, Tuple
from wiverno.core.requests import Request

logger = logging.getLogger(__name__)


class PageNotFound404:
    def __call__(self, request=None) -> tuple[str, str]:
        return "404 WHAT", "Page not found"


class Wiverno:
    """
    A simple WSGI-compatible web framework.
    """

    def __init__(
        self,
        routes_list: List[Tuple[str, Callable[[Request], Tuple[str, str]]]],
        page_404: Callable[[Request], Tuple[str, str]] = PageNotFound404(),
    ):
        """
        Initializes the Wiverno application with a list of routes.

        Args:
            routes_list: List of tuples (path, view-function).
            page_404: Callable to handle 404 errors.
        """
        self.routes_list: Dict[str, Callable[[Request], Tuple[str, str]]] = dict(routes_list)
        self.page_404 = page_404

    def __call__(self, environ: dict, start_response: Callable[[str, List[Tuple[str, str]]], None]) -> List[bytes]:
        request = Request(environ)
        try:
            view = self.routes_list.get(request.path, self.page_404)
            status, body = view(request)
        except Exception as e:
            logger.exception("Unhandled exception in view handler")
            status = "500 INTERNAL SERVER ERROR"
            body = "<h1>Internal Server Error</h1>"

        start_response(status, [("Content-Type", "text/html; charset=utf-8")])
        return [body.encode("utf-8")]
