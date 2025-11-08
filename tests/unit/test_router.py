"""
Unit tests for Router class.

Tests:
- Route registration via decorators
- HTTP methods (GET, POST, PUT, DELETE, etc.)
- Programmatic route addition
- Internal data structure
"""

import pytest

from wiverno.core.router import Router

# ============================================================================
# Router Initialization Tests
# ============================================================================


@pytest.mark.unit
class TestRouterInitialization:
    """Router initialization tests."""

    def test_router_initialization(self):
        """Test: Router should initialize with empty route list."""
        router = Router()

        assert router._routes == []
        assert isinstance(router._routes, list)

    def test_router_routes_is_list(self):
        """Test: _routes should be a list."""
        router = Router()
        assert isinstance(router._routes, list)


# ============================================================================
# route() Decorator Tests
# ============================================================================


@pytest.mark.unit
class TestRouteDecorator:
    """Basic route() decorator tests."""

    def test_route_decorator_basic(self, router):
        """Test: route() decorator should register a route."""

        @router.route("/test")
        def test_handler(request):
            return "200 OK", "Test"

        # Check that the route was added
        assert len(router._routes) == 1
        assert router._routes[0]["path"] == "/test"
        assert router._routes[0]["handler"] == test_handler
        assert router._routes[0]["methods"] is None  # Default None = all methods

    def test_route_decorator_with_methods(self, router):
        """Test: route() decorator should preserve specified methods."""

        @router.route("/api/users", methods=["GET", "POST"])
        def users_handler(request):
            return "200 OK", "Users"

        # Check methods
        assert router._routes[0]["methods"] == ["GET", "POST"]

    def test_route_decorator_returns_function(self, router):
        """Test: Decorator should return the original function."""

        def original_function(request):
            return "200 OK", "Original"

        decorated = router.route("/test")(original_function)

        # Check that the same function was returned
        assert decorated is original_function

    def test_multiple_routes(self, router):
        """Test: Multiple routes can be registered."""

        @router.route("/first")
        def first(request):
            return "200 OK", "First"

        @router.route("/second")
        def second(request):
            return "200 OK", "Second"

        @router.route("/third")
        def third(request):
            return "200 OK", "Third"

        # Check number of routes
        assert len(router._routes) == 3

        # Check paths
        paths = [route["path"] for route in router._routes]
        assert "/first" in paths
        assert "/second" in paths
        assert "/third" in paths


# ============================================================================
# HTTP Methods Tests (GET, POST, PUT, DELETE, etc.)
# ============================================================================


@pytest.mark.unit
class TestHTTPMethods:
    """Tests for various HTTP method decorators."""

    def test_get_method(self, router):
        """Test: get() decorator should register GET route."""

        @router.get("/users")
        def get_users(request):
            return "200 OK", "Users list"

        assert len(router._routes) == 1
        assert router._routes[0]["path"] == "/users"
        assert router._routes[0]["methods"] == ["GET"]

    def test_post_method(self, router):
        """Test: post() decorator should register POST route."""

        @router.post("/users")
        def create_user(request):
            return "201 Created", "User created"

        assert router._routes[0]["methods"] == ["POST"]

    def test_put_method(self, router):
        """Test: put() decorator should register PUT route."""

        @router.put("/users/1")
        def update_user(request):
            return "200 OK", "User updated"

        assert router._routes[0]["methods"] == ["PUT"]

    def test_patch_method(self, router):
        """Test: patch() decorator should register PATCH route."""

        @router.patch("/users/1")
        def patch_user(request):
            return "200 OK", "User patched"

        assert router._routes[0]["methods"] == ["PATCH"]

    def test_delete_method(self, router):
        """Test: delete() decorator should register DELETE route."""

        @router.delete("/users/1")
        def delete_user(request):
            return "204 No Content", ""

        assert router._routes[0]["methods"] == ["DELETE"]

    def test_connect_method(self, router):
        """Test: connect() decorator should register CONNECT route."""

        @router.connect("/tunnel")
        def connect_tunnel(request):
            return "200 OK", "Connected"

        assert router._routes[0]["methods"] == ["CONNECT"]

    def test_head_method(self, router):
        """Test: head() decorator should register HEAD route."""

        @router.head("/status")
        def head_status(request):
            return "200 OK", ""

        assert router._routes[0]["methods"] == ["HEAD"]

    def test_options_method(self, router):
        """Test: options() decorator should register OPTIONS route."""

        @router.options("/api")
        def options_api(request):
            return "200 OK", "OPTIONS"

        assert router._routes[0]["methods"] == ["OPTIONS"]

    def test_trace_method(self, router):
        """Test: trace() decorator should register TRACE route."""

        @router.trace("/trace")
        def trace_request(request):
            return "200 OK", "TRACE"

        assert router._routes[0]["methods"] == ["TRACE"]


# ============================================================================
# add_route() Tests - Programmatic Route Addition
# ============================================================================


@pytest.mark.unit
class TestAddRoute:
    """Tests for add_route() method for programmatic route addition."""

    def test_add_route_basic(self, router):
        """Test: add_route() should add route programmatically."""

        def handler(request):
            return "200 OK", "Handler"

        router.add_route("/programmatic", handler)

        # Check that route was added
        assert len(router._routes) == 1
        assert router._routes[0]["path"] == "/programmatic"
        assert router._routes[0]["handler"] == handler
        assert router._routes[0]["methods"] is None

    def test_add_route_with_methods(self, router):
        """Test: add_route() should preserve specified methods."""

        def handler(request):
            return "200 OK", "Handler"

        router.add_route("/api/data", handler, methods=["GET", "POST"])

        # Check methods
        assert router._routes[0]["methods"] == ["GET", "POST"]

    def test_add_multiple_routes_programmatically(self, router):
        """Test: Multiple routes can be added via add_route()."""

        def handler1(request):
            return "200 OK", "Handler 1"

        def handler2(request):
            return "200 OK", "Handler 2"

        router.add_route("/first", handler1, methods=["GET"])
        router.add_route("/second", handler2, methods=["POST"])

        # Check count
        assert len(router._routes) == 2

        # Check content
        assert router._routes[0]["path"] == "/first"
        assert router._routes[1]["path"] == "/second"


# ============================================================================
# Router Integration Tests
# ============================================================================


@pytest.mark.integration
class TestRouterIntegration:
    """Integration tests for combined Router usage."""

    def test_mixed_registration_methods(self, router):
        """Test: Decorators and add_route() can be mixed."""

        @router.get("/decorated")
        def decorated_handler(request):
            return "200 OK", "Decorated"

        def programmatic_handler(request):
            return "200 OK", "Programmatic"

        router.add_route("/programmatic", programmatic_handler, methods=["POST"])

        # Check both routes
        assert len(router._routes) == 2
        paths = [route["path"] for route in router._routes]
        assert "/decorated" in paths
        assert "/programmatic" in paths

    def test_same_path_different_methods(self, router):
        """Test: Same path can have different handlers for different methods."""

        @router.get("/api/resource")
        def get_resource(request):
            return "200 OK", "GET"

        @router.post("/api/resource")
        def create_resource(request):
            return "201 Created", "POST"

        @router.delete("/api/resource")
        def delete_resource(request):
            return "204 No Content", ""

        # All three should be registered
        assert len(router._routes) == 3

        # Check that all have the same path but different methods
        for route in router._routes:
            assert route["path"] == "/api/resource"

        methods = [route["methods"][0] for route in router._routes]
        assert "GET" in methods
        assert "POST" in methods
        assert "DELETE" in methods

    def test_router_with_complex_paths(self, router):
        """Test: Router should correctly handle complex paths."""

        @router.get("/api/v1/users/<user_id>/posts/<post_id>")
        def get_user_post(request, user_id, post_id):
            return "200 OK", f"User {user_id}, Post {post_id}"

        @router.post("/api/v2/organizations/<org_id>/members")
        def add_member(request, org_id):
            return "201 Created", f"Added to {org_id}"

        # Check that paths are saved correctly
        assert len(router._routes) == 2
        paths = [route["path"] for route in router._routes]
        assert "/api/v1/users/<user_id>/posts/<post_id>" in paths
        assert "/api/v2/organizations/<org_id>/members" in paths


# ============================================================================
# Edge Cases and Boundary Conditions
# ============================================================================


@pytest.mark.unit
class TestRouterEdgeCases:
    """Tests for edge cases and special situations."""

    def test_empty_path(self, router):
        """Test: Route with empty path can be registered."""

        @router.get("")
        def empty_path_handler(request):
            return "200 OK", "Empty"

        assert router._routes[0]["path"] == ""

    def test_root_path(self, router):
        """Test: Root path should be registered."""

        @router.get("/")
        def root_handler(request):
            return "200 OK", "Root"

        assert router._routes[0]["path"] == "/"

    def test_path_with_special_characters(self, router):
        """Test: Paths with special characters."""

        @router.get("/api/search?query=test")
        def search_handler(request):
            return "200 OK", "Search"

        # Path should be saved as is
        assert router._routes[0]["path"] == "/api/search?query=test"

    def test_handler_without_request_parameter(self, router):
        """Test: Handler can omit request parameter."""

        @router.get("/no-param")
        def no_param_handler():
            return "200 OK", "No param"

        # Route should be registered
        assert len(router._routes) == 1

    def test_lambda_as_handler(self, router):
        """Test: Lambda function can be a handler."""

        router.add_route("/lambda", lambda req: ("200 OK", "Lambda"))

        # Check that lambda is registered
        assert len(router._routes) == 1
        assert callable(router._routes[0]["handler"])
