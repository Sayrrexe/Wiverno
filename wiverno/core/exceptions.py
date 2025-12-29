"""
Core exceptions for the Wiverno framework.

This module defines custom exceptions used throughout the framework
for error handling and control flow.
"""


class RouteConflictError(Exception):
    """
    Exception raised when attempting to register a route that conflicts with an existing route.

    A conflict occurs when:
    - The same path and HTTP method combination is already registered
    - Overlapping method sets are registered for the same path
    """

class InvalidHTTPStatusError(Exception):
    """
    Raised when a view or middleware returns an HTTP status that cannot be used in a WSGI response.

    In a well‑behaved WSGI application the first element of the tuple returned by a view must be a string
    containing a *status line* – for example ``"200 OK"``, ``"404 Not Found"``, etc.
    The status line is split into two parts: the numeric code and the reason phrase.
    If the status does not conform to this format (for instance it is an integer, an empty string,
    a tuple, or any other non‑string value) the framework cannot build a valid response and will
    raise :class:`InvalidHTTPStatusError`.  The exception carries the offending value in its ``status``
    attribute so that callers can log or transform it if they wish.
    """

    def __init__(self, status: str | None = None) -> None:
        """
        Initialize the exception with the invalid status value.

        Args:
            status: The invalid HTTP status value that was provided.
        """
        self.status = status if status is not None else "unknown"
        super().__init__(f"Invalid HTTP status: {self.status!r}")
