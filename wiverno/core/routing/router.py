from wiverno.core.routing.base import RouterMixin
from wiverno.core.routing.registry import RouterRegistry


class Router(RouterMixin):
    """
    A standalone router for organizing and grouping related routes.

    Router instances can be included in the main application with a prefix
    to create modular route structures. Each router maintains its own
    RouterRegistry for route storage and matching.
    """


    def __init__(self) -> None:
        """
        Initialize a new Router with an empty route registry.
        """
        self.__registry = RouterRegistry()

    @property
    def _registry(self) -> RouterRegistry:
        """
        Get the RouterRegistry instance for this router.

        Returns:
            RouterRegistry: The registry that stores and matches routes.
        """
        return self.__registry
