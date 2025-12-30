from collections.abc import Callable
from typing import Any, ClassVar

from wiverno.core.requests import Request
from wiverno.core.exceptions import RouteConflictError
from wiverno.core.routing.patterns import PathPattern, compile_path


type Handler = Callable[[Request], tuple[str, str]]


class RouterRegistry:
    """
    Manages route registration, storage, and matching for a router.

    The registry maintains two separate collections:
    - Static routes: Direct path-to-handler mappings (faster lookup)
    - Dynamic routes: Path patterns with parameters (regex-based matching)

    Routes are automatically categorized based on whether they contain
    parameter placeholders (e.g., {id}, {name:int}).

    Attributes:
        HTTP_METHODS: List of valid HTTP method names.
    """

    HTTP_METHODS: ClassVar[list[str]] = [
        "GET",
        "POST",
        "PUT",
        "DELETE",
        "PATCH",
        "OPTIONS",
        "HEAD",
        "TRACE",
        "CONNECT",
    ]

    def __init__(self) -> None:
        """
        Initialize an empty route registry.
        """
        self._static_routes: dict[str, dict[str, Handler]] = {}
        self._dynamic_routes: list[tuple[PathPattern, dict[str, Handler]]] = []

    def register(self, path: str, handler: Handler, methods: list[str] | None = None) -> None:
        """
        Register a route handler for the specified path and HTTP methods.

        Args:
            path: URL path pattern. Static paths (e.g., "/users") or dynamic
                  paths with parameters (e.g., "/users/{id:int}").
            handler: The callable that handles requests to this route.
            methods: List of allowed HTTP methods. If None, allows all methods.

        Raises:
            ValueError: If methods contains invalid HTTP method names.
            RouteConflictError: If a handler is already registered for the same
                                path and method combination.
        """
        normalized_path = self._normalize_path(path)

        if methods is not None:
            invalid = set(methods) - set(self.HTTP_METHODS)
            if invalid:
                raise ValueError(f"Invalid HTTP methods: {invalid}")

        if "{" in path or "<" in path:
            self._register_dynamic(normalized_path, handler, methods)
        else:
            self._register_static(normalized_path, handler, methods)

    def match(
        self, path: str, method: str
    ) -> tuple[Handler | None, dict[str, Any] | None, bool | None]:
        """
        Find a handler for the given path and HTTP method.

        Args:
            path: The request path to match.
            method: The HTTP method (e.g., "GET", "POST").

        Returns:
            A tuple of (handler, path_params, method_allowed):
            - handler: The matching handler function, or None if no route found.
            - path_params: Dictionary of extracted path parameters (for dynamic routes),
                          or None for static routes.
            - method_allowed: True if path exists and method is allowed,
                             False if path exists but method is not allowed,
                             None if path does not exist at all.
        """
        normalized_path = self._normalize_path(path)

        if normalized_path in self._static_routes:
            handler = self._static_routes[normalized_path].get(method)
            if handler:
                return handler, None, True
            return None, None, False

        for pattern, methods_dict in self._dynamic_routes:
            match_result = pattern.match(normalized_path)
            if match_result:
                handler = methods_dict.get(method)
                if handler:
                    return handler, match_result, True
                return None, None, False

        return None, None, None

    def get_allowed_methods(self, path: str) -> set[str] | None:
        """
        Get the set of allowed HTTP methods for a given path.

        Args:
            path: The request path to check.

        Returns:
            A set of allowed HTTP method names, or None if the path doesn't exist.
        """
        normalized_path = self._normalize_path(path)

        if normalized_path in self._static_routes:
            return set(self._static_routes[normalized_path].keys())

        for pattern, methods_dict in self._dynamic_routes:
            if pattern.match(normalized_path):
                return set(methods_dict.keys())

        return None

    def merge_from(self, other: "RouterRegistry", prefix: str = "") -> None:
        """
        Merge routes from another registry into this one, optionally with a prefix.

        This is used when including a Router into the main application with
        app.include_router(router, prefix="/api").

        Args:
            other: The RouterRegistry to merge routes from.
            prefix: Optional path prefix to prepend to all merged routes.
                   Leading/trailing slashes are handled automatically.

        Raises:
            RouteConflictError: If any route from 'other' conflicts with
                               existing routes in this registry.
        """
        if prefix:
            prefix = self._normalize_path(prefix)
            if prefix == "/":
                prefix = ""

        for path, methods_dict in other.static_routes.items():
            full_path = prefix + path if prefix else path
            full_path = self._normalize_path(full_path)  # Normalize after concatenation

            if full_path not in self._static_routes:
                self._static_routes[full_path] = {}

            for method, handler in methods_dict.items():
                if method in self._static_routes[full_path]:
                    raise RouteConflictError(f"Handler for {method} {full_path} already registered")
                self._static_routes[full_path][method] = handler

        for pattern, methods_dict in other.dynamic_routes:
            new_pattern = pattern.with_prefix(prefix) if prefix else pattern

            for existing_pattern, existing_methods in self._dynamic_routes:
                if existing_pattern.pattern_str == new_pattern.pattern_str:
                    existing_method_set = set(existing_methods.keys())
                    new_method_set = set(methods_dict.keys())
                    conflicts = existing_method_set & new_method_set

                    if conflicts:
                        conflict_list = ", ".join(sorted(conflicts))
                        raise RouteConflictError(
                            f"Handler for {conflict_list} {new_pattern.pattern_str} already registered"
                        )

            self._dynamic_routes.append((new_pattern, methods_dict))

        self._sort_dynamic_routes()

    def _register_static(
        self, path: str, handler: Handler, methods: list[str] | None = None
    ) -> None:
        """
        Register a static route (no path parameters).

        Args:
            path: Normalized static path.
            handler: The handler function.
            methods: List of HTTP methods, or None for all methods.

        Raises:
            RouteConflictError: If handler already exists for path/method, or if
                               there are overlapping method registrations.
        """
        if path not in self._static_routes:
            self._static_routes[path] = {}

        methods_to_register = self.HTTP_METHODS if methods is None else methods

        existing_methods = set(self._static_routes[path].keys())
        new_methods = set(methods_to_register)
        conflicts = existing_methods & new_methods

        if conflicts:
            conflict_list = ", ".join(sorted(conflicts))
            raise RouteConflictError(f"Handler for {conflict_list} {path} already registered")

        for method in methods_to_register:
            self._static_routes[path][method] = handler

    def _register_dynamic(
        self, path: str, handler: Handler, methods: list[str] | None = None
    ) -> None:
        """
        Register a dynamic route (with path parameters).

        Args:
            path: Normalized path pattern with parameters (e.g., "/users/{id:int}").
            handler: The handler function.
            methods: List of HTTP methods, or None for all methods.

        Raises:
            RouteConflictError: If the same pattern with overlapping methods already exists.
        """
        pattern = compile_path(path)
        methods_to_register = self.HTTP_METHODS if methods is None else methods

        # Check if pattern already exists
        for existing_pattern, existing_methods in self._dynamic_routes:
            if existing_pattern.pattern_str == pattern.pattern_str:
                # Pattern exists, check for method conflicts
                existing_method_set = set(existing_methods.keys())
                new_method_set = set(methods_to_register)
                conflicts = existing_method_set & new_method_set

                if conflicts:
                    conflict_list = ", ".join(sorted(conflicts))
                    raise RouteConflictError(
                        f"Handler for {conflict_list} {path} already registered"
                    )

                # No conflicts, add new methods to existing pattern
                for method in methods_to_register:
                    existing_methods[method] = handler
                return

        # Pattern doesn't exist, create new entry
        methods_dict = {}
        for method in methods_to_register:
            methods_dict[method] = handler

        self._dynamic_routes.append((pattern, methods_dict))
        self._sort_dynamic_routes()

    def _sort_dynamic_routes(self) -> None:
        self._dynamic_routes.sort(
            key=lambda x: (x[0].segments_count, x[0].pattern_str),
            reverse=True,
        )

    @property
    def static_routes(self) -> dict[str, dict[str, Handler]]:
        """
        Public read-only access to static routes.

        Returns:
            Dictionary mapping paths to methods to handlers.
        """
        return self._static_routes

    @property
    def dynamic_routes(self) -> list[tuple[PathPattern, dict[str, Handler]]]:
        """
        Public read-only access to dynamic routes.

        Returns:
            List of (pattern, methods_dict) tuples.
        """
        return self._dynamic_routes

    @staticmethod
    def normalize_path(path: str) -> str:
        """
        Normalize a URL path to a canonical form.

        Rules:
        - Empty path becomes "/"
        - Ensures path starts with "/"
        - Removes trailing "/" except for root path
        - Strips leading/trailing whitespace

        Args:
            path: The path to normalize.

        Returns:
            The normalized path.
        """
        if not path:
            return "/"

        path = "/" + path.strip("/")

        if path != "/":
            path = path.rstrip("/")

        return path

    @staticmethod
    def _normalize_path(path: str) -> str:
        """
        Internal wrapper for normalize_path.

        Args:
            path: The path to normalize.

        Returns:
            The normalized path.
        """
        return RouterRegistry.normalize_path(path)
