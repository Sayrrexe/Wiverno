import logging
import traceback
from collections.abc import Callable
from pathlib import Path
from typing import Any

from wiverno.core.requests import Request
from wiverno.core.routing.base import RouterMixin
from wiverno.core.routing.registry import RouterRegistry
from wiverno.core.routing.router import Router
from wiverno.templating.templator import Templator

logger = logging.getLogger(__name__)

type Handler = Callable[[Request], tuple[str, str]]
type ErrorHandler = Callable[[Request, str | None], tuple[str, str]]


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_TEMPLATE_PATH = BASE_DIR / "static" / "templates"


class PageNotFound404:
    """
    Default 404 error handler that renders the error_404.html template.
    """

    def __call__(self, _request: Request) -> tuple[str, str]:
        """
        Handles 404 Not Found errors.

        Args:
            request (Request): The incoming request object.

        Returns:
            tuple[str, str]: A tuple of (status, html_body).
        """
        templator = Templator(folder=DEFAULT_TEMPLATE_PATH)
        return "404 NOT FOUND", templator.render("error_404.html")


class MethodNotAllowed405:
    """
    Default 405 error handler that renders the error_405.html template.
    """

    def __call__(self, request: Request) -> tuple[str, str]:
        """
        Handles 405 Method Not Allowed errors.

        Args:
            request (Request): The incoming request object.

        Returns:
            tuple[str, str]: A tuple of (status, html_body).
        """
        templator = Templator(folder=DEFAULT_TEMPLATE_PATH)
        return "405 METHOD NOT ALLOWED", templator.render(
            "error_405.html", content={"method": request.method}
        )


class InternalServerError500:
    """
    Default 500 error handler that renders the error_500.html template.
    """

    def __call__(self, _request: Request, error_traceback: str | None = None) -> tuple[str, str]:
        """
        Handles 500 Internal Server Error.

        Args:
            request (Request): The incoming request object.
            error_traceback (str, optional): The traceback string if debug mode is enabled.

        Returns:
            tuple[str, str]: A tuple of (status, html_body).
        """
        templator = Templator(folder=DEFAULT_TEMPLATE_PATH)
        return "500 INTERNAL SERVER ERROR", templator.render(
            "error_500.html", content={"traceback": error_traceback}
        )


class Wiverno(RouterMixin):
    """
    A simple WSGI-compatible web framework.
    """

    def __init__(
        self,
        debug_mode: bool = True,
        system_template_path: str = str(DEFAULT_TEMPLATE_PATH),
        page_404: Callable[[Request], tuple[str, str]] = PageNotFound404(),
        page_405: Callable[[Request], tuple[str, str]] = MethodNotAllowed405(),
        page_500: Callable[[Request, str | None], tuple[str, str]] = InternalServerError500(),
    ) -> None:
        """
        Initializes the Wiverno application with a list of routes.

        Args:
            debug_mode: Enable or disable debug mode (default is True).
            system_template_path: Path to base templates used for error pages.
            page_404: Callable to handle 404 errors (optional).
            page_405: Callable to handle 405 errors (optional).
            page_500: Callable to handle 500 errors (optional).
        """
        self.__registry = RouterRegistry()

        self.system_templator = Templator(folder=system_template_path)
        self.debug = debug_mode
        self.page_404 = page_404
        self.page_405 = page_405
        self.page_500 = page_500

    @property
    def _registry(self) -> RouterRegistry:
        """
        Get the RouterRegistry instance for this application.

        Returns:
            RouterRegistry: The registry that stores and matches routes.
        """
        return self.__registry

    def include_router(self, router: Router, prefix: str = "") -> None:
        """
        Include routes from a Router instance into this application.

        Args:
            router: The Router instance whose routes should be included.
            prefix: Optional path prefix to prepend to all routes from the router.
                   For example, prefix="/api" will make router routes accessible
                   under /api/... paths.
        """
        self.__registry.merge_from(router.registry, prefix)

    def __call__(
        self, environ: dict[str, Any], start_response: Callable[[str, list[tuple[str, str]]], None]
    ) -> list[bytes]:
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

        try:
            handler, path_params, method_allowed = self.__registry.match(
                request.path,
                request.method,
            )

            if path_params:
                request.path_params = path_params

            if handler is None and method_allowed is None:
                status, body = self.page_404(request)
            elif handler is None and method_allowed is False:
                status, body = self.page_405(request)
            else:
                status, body = handler(request)  # type: ignore

        except Exception:
            logger.exception("Unhandled exception in view handler")
            error_traceback = traceback.format_exc() if self.debug else None
            status, body = self.page_500(request, error_traceback)

        start_response(status, [("Content-Type", "text/html; charset=utf-8")])
        return [body.encode("utf-8")]
