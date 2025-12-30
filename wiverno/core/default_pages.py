import logging

from wiverno.core.config import WivernoConfig
from wiverno.core.requests import Request
from wiverno.templating.templator import Templator

logger = logging.getLogger(__name__)

TEMPLATE_PATH = WivernoConfig.DEFAULT_TEMPLATE_PATH


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
        templator = Templator(folder=TEMPLATE_PATH)
        return 404, templator.render("error_404.html")


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
        templator = Templator(folder=TEMPLATE_PATH)
        return 405, templator.render(
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
        templator = Templator(folder=TEMPLATE_PATH)
        return 500, templator.render(
            "error_500.html", content={"traceback": error_traceback}
        )
