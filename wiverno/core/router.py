from collections.abc import Callable
from typing import Any


class Router:
    """
    A router class for organizing and grouping routes.
    Routes can be included in a Wiverno application using include_router().
    """

    def __init__(self) -> None:
        """
        Initializes an empty router.
        """
        self._routes: list[dict[str, Any]] = []

    def route(
        self, path: str, methods: list[str] | None = None
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """
        Decorator to register a route with the router.

        Args:
            path (str): The URL path for the route.
            methods (Optional[List[str]]): Allowed HTTP methods for this route.
                If None, defaults to ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'].

        Returns:
            Callable: The decorator function.
        """

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self._routes.append({"path": path, "handler": func, "methods": methods})
            return func

        return decorator

    def get(self, path: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """
        Decorator to register a GET route.

        Args:
            path (str): The URL path for the route.

        Returns:
            Callable: The decorator function.
        """
        return self.route(path, methods=["GET"])

    def post(self, path: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """
        Decorator to register a POST route.

        Args:
            path (str): The URL path for the route.

        Returns:
            Callable: The decorator function.
        """
        return self.route(path, methods=["POST"])

    def put(self, path: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """
        Decorator to register a PUT route.

        Args:
            path (str): The URL path for the route.

        Returns:
            Callable: The decorator function.
        """
        return self.route(path, methods=["PUT"])

    def patch(self, path: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """
        Decorator to register a PATCH route.

        Args:
            path (str): The URL path for the route.

        Returns:
            Callable: The decorator function.
        """
        return self.route(path, methods=["PATCH"])

    def delete(self, path: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """
        Decorator to register a DELETE route.

        Args:
            path (str): The URL path for the route.

        Returns:
            Callable: The decorator function.
        """
        return self.route(path, methods=["DELETE"])

    def connect(self, path: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """
        Decorator to register a CONNECT route.

        Args:
            path (str): The URL path for the route.

        Returns:
            Callable: The decorator function.
        """
        return self.route(path, methods=["CONNECT"])

    def head(self, path: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """
        Decorator to register a HEAD route.

        Args:
            path (str): The URL path for the route.

        Returns:
            Callable: The decorator function.
        """
        return self.route(path, methods=["HEAD"])

    def options(self, path: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """
        Decorator to register an OPTIONS route.

        Args:
            path (str): The URL path for the route.

        Returns:
            Callable: The decorator function.
        """
        return self.route(path, methods=["OPTIONS"])

    def trace(self, path: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """
        Decorator to register a TRACE route.

        Args:
            path (str): The URL path for the route.

        Returns:
            Callable: The decorator function.
        """
        return self.route(path, methods=["TRACE"])

    def add_route(
        self, path: str, handler: Callable[..., Any], methods: list[str] | None = None
    ) -> None:
        """
        Programmatically adds a route to the router.

        Args:
            path (str): The URL path for the route.
            handler (Callable): The view function to handle the route.
            methods (Optional[List[str]]): Allowed HTTP methods for this route.
                If None, no method restriction is applied.
        """
        self._routes.append({"path": path, "handler": handler, "methods": methods})

    def get_routes(self) -> list[dict[str, Any]]:
        """
        Returns the list of registered routes.

        Returns:
            list[dict]: List of route dictionaries containing path, handler, and methods.
        """
        return self._routes
