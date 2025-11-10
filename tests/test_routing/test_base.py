"""
Unit tests for RouterMixin abstract base class.

Tests:
- HTTP method decorators (get, post, put, patch, delete, etc.)
- Route decorator functionality
- Handler registration
"""

import pytest

from wiverno.core.requests import Request
from wiverno.core.routing.router import Router


# ============================================================================
# RouterMixin Decorator Tests
# ============================================================================


@pytest.mark.unit
class TestRouterMixinDecorators:
    """Tests for RouterMixin HTTP method decorators."""

    def test_route_decorator(self):
        """Test: route() decorator registers handler."""
        router = Router()

        @router.route("/users")
        def handler(request: Request) -> tuple[str, str]:
            return "200 OK", "Users"

        matched_handler, params, allowed = router._registry.match("/users", "GET")
        
        assert matched_handler == handler
        assert allowed is True

    def test_route_decorator_with_methods(self):
        """Test: route() decorator with specific methods."""
        router = Router()

        @router.route("/users", methods=["GET", "POST"])
        def handler(request: Request) -> tuple[str, str]:
            return "200 OK", "Users"

        # Should match GET
        matched_handler, params, allowed = router._registry.match("/users", "GET")
        assert matched_handler == handler

        # Should match POST
        matched_handler, params, allowed = router._registry.match("/users", "POST")
        assert matched_handler == handler

        # Should not match PUT
        matched_handler, params, allowed = router._registry.match("/users", "PUT")
        assert matched_handler is None
        assert allowed is False

    def test_get_decorator(self):
        """Test: get() decorator registers GET route."""
        router = Router()

        @router.get("/users")
        def handler(request: Request) -> tuple[str, str]:
            return "200 OK", "GET Users"

        matched_handler, params, allowed = router._registry.match("/users", "GET")
        
        assert matched_handler == handler
        
        # Should not match POST
        matched_handler, params, allowed = router._registry.match("/users", "POST")
        assert matched_handler is None
        assert allowed is False

    def test_post_decorator(self):
        """Test: post() decorator registers POST route."""
        router = Router()

        @router.post("/users")
        def handler(request: Request) -> tuple[str, str]:
            return "201 Created", "User created"

        matched_handler, params, allowed = router._registry.match("/users", "POST")
        
        assert matched_handler == handler

    def test_put_decorator(self):
        """Test: put() decorator registers PUT route."""
        router = Router()

        @router.put("/users/{id}")
        def handler(request: Request) -> tuple[str, str]:
            return "200 OK", "User updated"

        matched_handler, params, allowed = router._registry.match("/users/1", "PUT")
        
        assert matched_handler == handler

    def test_patch_decorator(self):
        """Test: patch() decorator registers PATCH route."""
        router = Router()

        @router.patch("/users/{id}")
        def handler(request: Request) -> tuple[str, str]:
            return "200 OK", "User patched"

        matched_handler, params, allowed = router._registry.match("/users/1", "PATCH")
        
        assert matched_handler == handler

    def test_delete_decorator(self):
        """Test: delete() decorator registers DELETE route."""
        router = Router()

        @router.delete("/users/{id}")
        def handler(request: Request) -> tuple[str, str]:
            return "204 No Content", ""

        matched_handler, params, allowed = router._registry.match("/users/1", "DELETE")
        
        assert matched_handler == handler

    def test_head_decorator(self):
        """Test: head() decorator registers HEAD route."""
        router = Router()

        @router.head("/status")
        def handler(request: Request) -> tuple[str, str]:
            return "200 OK", ""

        matched_handler, params, allowed = router._registry.match("/status", "HEAD")
        
        assert matched_handler == handler

    def test_options_decorator(self):
        """Test: options() decorator registers OPTIONS route."""
        router = Router()

        @router.options("/api")
        def handler(request: Request) -> tuple[str, str]:
            return "200 OK", "OPTIONS"

        matched_handler, params, allowed = router._registry.match("/api", "OPTIONS")
        
        assert matched_handler == handler

    def test_connect_decorator(self):
        """Test: connect() decorator registers CONNECT route."""
        router = Router()

        @router.connect("/tunnel")
        def handler(request: Request) -> tuple[str, str]:
            return "200 OK", "Connected"

        matched_handler, params, allowed = router._registry.match("/tunnel", "CONNECT")
        
        assert matched_handler == handler

    def test_trace_decorator(self):
        """Test: trace() decorator registers TRACE route."""
        router = Router()

        @router.trace("/debug")
        def handler(request: Request) -> tuple[str, str]:
            return "200 OK", "TRACE"

        matched_handler, params, allowed = router._registry.match("/debug", "TRACE")
        
        assert matched_handler == handler


# ============================================================================
# Decorator Return Value Tests
# ============================================================================


@pytest.mark.unit
class TestDecoratorReturnValue:
    """Tests that decorators return the original function."""

    def test_route_decorator_returns_function(self):
        """Test: route() decorator returns original function."""
        router = Router()

        def original_handler(request: Request) -> tuple[str, str]:
            return "200 OK", "Test"

        decorated = router.route("/test")(original_handler)

        assert decorated is original_handler

    def test_get_decorator_returns_function(self):
        """Test: get() decorator returns original function."""
        router = Router()

        def original_handler(request: Request) -> tuple[str, str]:
            return "200 OK", "Test"

        decorated = router.get("/test")(original_handler)

        assert decorated is original_handler

    def test_decorator_preserves_function_metadata(self):
        """Test: Decorator preserves function name and docstring."""
        router = Router()

        @router.get("/test")
        def my_handler(request: Request) -> tuple[str, str]:
            """Handler docstring."""
            return "200 OK", "Test"

        assert my_handler.__name__ == "my_handler"
        assert my_handler.__doc__ == "Handler docstring."


# ============================================================================
# Multiple Route Registration Tests
# ============================================================================


@pytest.mark.unit
class TestMultipleRouteRegistration:
    """Tests for registering multiple routes."""

    def test_register_multiple_routes(self):
        """Test: Multiple routes can be registered."""
        router = Router()

        @router.get("/users")
        def users_handler(request: Request) -> tuple[str, str]:
            return "200 OK", "Users"

        @router.get("/posts")
        def posts_handler(request: Request) -> tuple[str, str]:
            return "200 OK", "Posts"

        matched_handler, params, allowed = router._registry.match("/users", "GET")
        assert matched_handler == users_handler

        matched_handler, params, allowed = router._registry.match("/posts", "GET")
        assert matched_handler == posts_handler

    def test_same_path_different_methods(self):
        """Test: Same path with different methods."""
        router = Router()

        @router.get("/users")
        def get_users(request: Request) -> tuple[str, str]:
            return "200 OK", "GET Users"

        @router.post("/users")
        def create_user(request: Request) -> tuple[str, str]:
            return "201 Created", "POST User"

        matched_handler, params, allowed = router._registry.match("/users", "GET")
        assert matched_handler == get_users

        matched_handler, params, allowed = router._registry.match("/users", "POST")
        assert matched_handler == create_user

    def test_mix_static_and_dynamic_routes(self):
        """Test: Mix of static and dynamic routes."""
        router = Router()

        @router.get("/users")
        def list_users(request: Request) -> tuple[str, str]:
            return "200 OK", "All users"

        @router.get("/users/{id}")
        def get_user(request: Request) -> tuple[str, str]:
            return "200 OK", "One user"

        # Static route
        matched_handler, params, allowed = router._registry.match("/users", "GET")
        assert matched_handler == list_users
        assert params is None

        # Dynamic route
        matched_handler, params, allowed = router._registry.match("/users/42", "GET")
        assert matched_handler == get_user
        assert params == {"id": "42"}


# ============================================================================
# Dynamic Route Tests
# ============================================================================


@pytest.mark.unit
class TestDynamicRoutes:
    """Tests for dynamic route patterns."""

    def test_route_with_int_parameter(self):
        """Test: Route with int parameter."""
        router = Router()

        @router.get("/users/{id:int}")
        def handler(request: Request) -> tuple[str, str]:
            return "200 OK", "User"

        matched_handler, params, allowed = router._registry.match("/users/42", "GET")
        
        assert matched_handler == handler
        assert params == {"id": 42}
        assert isinstance(params["id"], int)

    def test_route_with_multiple_parameters(self):
        """Test: Route with multiple parameters."""
        router = Router()

        @router.get("/users/{user_id:int}/posts/{post_id:int}")
        def handler(request: Request) -> tuple[str, str]:
            return "200 OK", "Post"

        matched_handler, params, allowed = router._registry.match("/users/5/posts/10", "GET")
        
        assert matched_handler == handler
        assert params == {"user_id": 5, "post_id": 10}

    def test_route_with_string_parameter(self):
        """Test: Route with string parameter."""
        router = Router()

        @router.get("/tags/{name}")
        def handler(request: Request) -> tuple[str, str]:
            return "200 OK", "Tag"

        matched_handler, params, allowed = router._registry.match("/tags/python", "GET")
        
        assert matched_handler == handler
        assert params == {"name": "python"}
