from abc import ABC, abstractmethod
from collections.abc import Callable

from wiverno.core.requests import Request
from wiverno.core.routing.registry import RouterRegistry

type Handler = Callable[[Request], tuple[str, str]]


class RouterMixin(ABC):
    """
    A mixin class for routers that provides common routing functionality.

    This abstract base class defines the interface for route registration
    and delegates the actual storage to a concrete RouterRegistry implementation
    via the abstract _registry property.

    Subclasses must implement the _registry property to provide access
    to a RouterRegistry instance.
    """

    @property
    @abstractmethod
    def _registry(self) -> RouterRegistry:
        """
        Get the RouterRegistry instance for this router.

        Returns:
            RouterRegistry: The registry that stores and matches routes.

        Note:
            This is an abstract property that must be implemented by subclasses.
        """

    def route(self, path: str, methods: list[str] | None = None) -> Callable[[Handler], Handler]:
        """
        Register a route handler for the specified path and HTTP methods.

        Args:
            path: URL path pattern. Supports static paths (e.g., "/users") and
                  dynamic paths with parameters (e.g., "/users/{id:int}").
            methods: List of allowed HTTP methods (e.g., ["GET", "POST"]).
                     If None, the route will accept all HTTP methods.

        Returns:
            A decorator function that registers the handler and returns it unchanged.
        """

        def decorator(func: Handler) -> Handler:
            self._registry.register(path, func, methods)
            return func

        return decorator

    def get(self, path: str) -> Callable[[Handler], Handler]:
        """
        Register a GET route handler.

        Args:
            path: URL path pattern.

        Returns:
            A decorator function for the handler.
        """
        return self.route(path, methods=["GET"])

    def post(self, path: str) -> Callable[[Handler], Handler]:
        """
        Register a POST route handler.

        Args:
            path: URL path pattern.

        Returns:
            A decorator function for the handler.
        """
        return self.route(path, methods=["POST"])

    def put(self, path: str) -> Callable[[Handler], Handler]:
        """
        Register a PUT route handler.

        Args:
            path: URL path pattern.

        Returns:
            A decorator function for the handler.
        """
        return self.route(path, methods=["PUT"])

    def patch(self, path: str) -> Callable[[Handler], Handler]:
        """
        Register a PATCH route handler.

        Args:
            path: URL path pattern.

        Returns:
            A decorator function for the handler.
        """
        return self.route(path, methods=["PATCH"])

    def delete(self, path: str) -> Callable[[Handler], Handler]:
        """
        Register a DELETE route handler.

        Args:
            path: URL path pattern.

        Returns:
            A decorator function for the handler.
        """
        return self.route(path, methods=["DELETE"])

    def head(self, path: str) -> Callable[[Handler], Handler]:
        """
        Register a HEAD route handler.

        Args:
            path: URL path pattern.

        Returns:
            A decorator function for the handler.
        """
        return self.route(path, methods=["HEAD"])

    def options(self, path: str) -> Callable[[Handler], Handler]:
        """
        Register an OPTIONS route handler.

        Args:
            path: URL path pattern.

        Returns:
            A decorator function for the handler.
        """
        return self.route(path, methods=["OPTIONS"])

    def connect(self, path: str) -> Callable[[Handler], Handler]:
        """
        Register a CONNECT route handler.

        Args:
            path: URL path pattern.

        Returns:
            A decorator function for the handler.
        """
        return self.route(path, methods=["CONNECT"])

    def trace(self, path: str) -> Callable[[Handler], Handler]:
        """
        Register a TRACE route handler.

        Args:
            path: URL path pattern.

        Returns:
            A decorator function for the handler.
        """
        return self.route(path, methods=["TRACE"])
