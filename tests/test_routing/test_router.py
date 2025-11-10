"""
Unit tests for Router class.

Tests:
- Router initialization
- Route registration
- Router registry access
- Integration with RouterMixin
"""

import pytest

from wiverno.core.requests import Request
from wiverno.core.routing.registry import RouterRegistry
from wiverno.core.routing.router import Router


# ============================================================================
# Router Initialization Tests
# ============================================================================


@pytest.mark.unit
class TestRouterInitialization:
    """Tests for Router initialization."""

    def test_router_initialization(self):
        """Test: Router initializes with empty registry."""
        router = Router()

        assert isinstance(router._registry, RouterRegistry)

    def test_router_has_empty_registry(self):
        """Test: New router has empty registry."""
        router = Router()

        assert len(router._registry._static_routes) == 0
        assert len(router._registry._dynamic_routes) == 0

    def test_multiple_routers_independent(self):
        """Test: Multiple router instances are independent."""
        router1 = Router()
        router2 = Router()

        @router1.get("/users")
        def handler1(request: Request) -> tuple[str, str]:
            return "200 OK", "Router 1"

        # router2 should not have router1's routes
        matched_handler, params, allowed = router2._registry.match("/users", "GET")

        assert matched_handler is None
        assert allowed is None


# ============================================================================
# Router Registry Property Tests
# ============================================================================


@pytest.mark.unit
class TestRouterRegistryProperty:
    """Tests for Router._registry property."""

    def test_registry_property_returns_registry(self):
        """Test: _registry property returns RouterRegistry instance."""
        router = Router()

        registry = router._registry

        assert isinstance(registry, RouterRegistry)

    def test_registry_property_is_consistent(self):
        """Test: _registry property returns same instance."""
        router = Router()

        registry1 = router._registry
        registry2 = router._registry

        assert registry1 is registry2


# ============================================================================
# Router Integration Tests
# ============================================================================


@pytest.mark.unit
class TestRouterIntegration:
    """Integration tests for Router with RouterMixin."""

    def test_router_inherits_mixin_methods(self):
        """Test: Router inherits all RouterMixin decorator methods."""
        router = Router()

        # Check all HTTP method decorators exist
        assert hasattr(router, "route")
        assert hasattr(router, "get")
        assert hasattr(router, "post")
        assert hasattr(router, "put")
        assert hasattr(router, "patch")
        assert hasattr(router, "delete")
        assert hasattr(router, "head")
        assert hasattr(router, "options")
        assert hasattr(router, "connect")
        assert hasattr(router, "trace")

    def test_router_decorator_registration(self):
        """Test: Decorators register routes in router's registry."""
        router = Router()

        @router.get("/test")
        def handler(request: Request) -> tuple[str, str]:
            return "200 OK", "Test"

        matched_handler, params, allowed = router._registry.match("/test", "GET")

        assert matched_handler == handler

    def test_router_complex_route_registration(self):
        """Test: Router can register complex routes."""
        router = Router()

        @router.get("/users")
        def list_users(request: Request) -> tuple[str, str]:
            return "200 OK", "Users list"

        @router.post("/users")
        def create_user(request: Request) -> tuple[str, str]:
            return "201 Created", "User created"

        @router.get("/users/{id:int}")
        def get_user(request: Request) -> tuple[str, str]:
            return "200 OK", "User detail"

        @router.put("/users/{id:int}")
        def update_user(request: Request) -> tuple[str, str]:
            return "200 OK", "User updated"

        # Test all routes
        assert router._registry.match("/users", "GET")[0] == list_users
        assert router._registry.match("/users", "POST")[0] == create_user

        # Dynamic routes - need valid integers
        handler, params, allowed = router._registry.match("/users/123", "GET")
        assert handler == get_user
        assert params == {"id": 123}

        handler, params, allowed = router._registry.match("/users/456", "PUT")
        assert handler == update_user
        assert params == {"id": 456}


# ============================================================================
# Router Usage Examples Tests
# ============================================================================


@pytest.mark.unit
class TestRouterUsageExamples:
    """Tests demonstrating typical Router usage patterns."""

    def test_rest_api_pattern(self):
        """Test: Router supports REST API pattern."""
        router = Router()

        @router.get("/api/items")
        def list_items(request: Request) -> tuple[str, str]:
            return "200 OK", "[]"

        @router.post("/api/items")
        def create_item(request: Request) -> tuple[str, str]:
            return "201 Created", "{}"

        @router.get("/api/items/{id:int}")
        def get_item(request: Request) -> tuple[str, str]:
            return "200 OK", "{}"

        @router.put("/api/items/{id:int}")
        def update_item(request: Request) -> tuple[str, str]:
            return "200 OK", "{}"

        @router.delete("/api/items/{id:int}")
        def delete_item(request: Request) -> tuple[str, str]:
            return "204 No Content", ""

        # Verify all CRUD operations are registered
        assert router._registry.match("/api/items", "GET")[2] is True
        assert router._registry.match("/api/items", "POST")[2] is True

        # Dynamic routes need valid integers
        handler, params, allowed = router._registry.match("/api/items/123", "GET")
        assert allowed is True

        handler, params, allowed = router._registry.match("/api/items/456", "PUT")
        assert allowed is True

        handler, params, allowed = router._registry.match("/api/items/789", "DELETE")
        assert allowed is True

    def test_nested_resources_pattern(self):
        """Test: Router supports nested resources."""
        router = Router()

        @router.get("/users/{user_id:int}/posts")
        def get_user_posts(request: Request) -> tuple[str, str]:
            return "200 OK", "User posts"

        @router.get("/users/{user_id:int}/posts/{post_id:int}")
        def get_user_post(request: Request) -> tuple[str, str]:
            return "200 OK", "User post"

        handler1, params1, allowed1 = router._registry.match("/users/5/posts", "GET")
        handler2, params2, allowed2 = router._registry.match("/users/5/posts/10", "GET")

        assert handler1 == get_user_posts
        assert params1 == {"user_id": 5}

        assert handler2 == get_user_post
        assert params2 == {"user_id": 5, "post_id": 10}

    def test_versioned_api_pattern(self):
        """Test: Router supports API versioning."""
        router = Router()

        @router.get("/api/v1/users")
        def v1_users(request: Request) -> tuple[str, str]:
            return "200 OK", "V1 Users"

        @router.get("/api/v2/users")
        def v2_users(request: Request) -> tuple[str, str]:
            return "200 OK", "V2 Users"

        handler1, params1, allowed1 = router._registry.match("/api/v1/users", "GET")
        handler2, params2, allowed2 = router._registry.match("/api/v2/users", "GET")

        assert handler1 == v1_users
        assert handler2 == v2_users


# ============================================================================
# Edge Cases Tests
# ============================================================================


@pytest.mark.unit
class TestRouterEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_empty_router(self):
        """Test: Empty router returns None for any path."""
        router = Router()

        matched_handler, params, allowed = router._registry.match("/any/path", "GET")

        assert matched_handler is None
        assert params is None
        assert allowed is None

    def test_root_path_route(self):
        """Test: Router can handle root path."""
        router = Router()

        @router.get("/")
        def root_handler(request: Request) -> tuple[str, str]:
            return "200 OK", "Root"

        matched_handler, params, allowed = router._registry.match("/", "GET")

        assert matched_handler == root_handler

    def test_deep_nested_routes(self):
        """Test: Router handles deeply nested routes."""
        router = Router()

        @router.get("/a/b/c/d/e/f/g")
        def deep_handler(request: Request) -> tuple[str, str]:
            return "200 OK", "Deep"

        matched_handler, params, allowed = router._registry.match("/a/b/c/d/e/f/g", "GET")

        assert matched_handler == deep_handler

    def test_route_with_special_chars(self):
        """Test: Router handles routes with hyphens and underscores."""
        router = Router()

        @router.get("/api-v1/user_profile")
        def handler(request: Request) -> tuple[str, str]:
            return "200 OK", "Profile"

        matched_handler, params, allowed = router._registry.match("/api-v1/user_profile", "GET")

        assert matched_handler == handler
