"""
Unit tests for RouterRegistry class.

Tests:
- Route registration (static and dynamic)
- Route matching with O(1) for static routes
- HTTP method validation
- Route conflicts detection
- Registry merging
- Path normalization
"""

import pytest

from wiverno.core.routing.registry import RouterRegistry
from wiverno.core.exceptions import RouteConflictError

# ============================================================================
# Registration Tests
# ============================================================================


@pytest.mark.unit
class TestRouteRegistration:
    """Tests for route registration."""

    def test_register_static_route(self):
        """Test: Register simple static route."""
        registry = RouterRegistry()
        def handler(req):
            return ("200 OK", "Test")

        registry.register("/users", handler, methods=["GET"])

        assert "/users" in registry.static_routes
        assert "GET" in registry.static_routes["/users"]

    def test_register_dynamic_route(self):
        """Test: Register dynamic route with parameters."""
        registry = RouterRegistry()
        def handler(req):
            return ("200 OK", "Test")

        registry.register("/users/{id}", handler, methods=["GET"])

        assert len(registry.dynamic_routes) == 1
        pattern, methods = registry.dynamic_routes[0]
        assert pattern.pattern_str == "/users/{id}"
        assert "GET" in methods

    def test_register_all_methods(self):
        """Test: Register route for all HTTP methods (methods=None)."""
        registry = RouterRegistry()
        def handler(req):
            return ("200 OK", "Test")

        registry.register("/api/data", handler, methods=None)

        assert "GET" in registry.static_routes["/api/data"]
        assert "POST" in registry.static_routes["/api/data"]
        assert "PUT" in registry.static_routes["/api/data"]
        assert "DELETE" in registry.static_routes["/api/data"]

    def test_register_multiple_methods(self):
        """Test: Register route for multiple methods."""
        registry = RouterRegistry()
        def handler(req):
            return ("200 OK", "Test")

        registry.register("/api/users", handler, methods=["GET", "POST"])

        assert "GET" in registry.static_routes["/api/users"]
        assert "POST" in registry.static_routes["/api/users"]
        assert "PUT" not in registry.static_routes["/api/users"]

    def test_register_invalid_method(self):
        """Test: Reject invalid HTTP method."""
        registry = RouterRegistry()
        def handler(req):
            return ("200 OK", "Test")

        with pytest.raises(ValueError, match="Invalid HTTP methods"):
            registry.register("/users", handler, methods=["INVALID"])

    def test_register_normalizes_path(self):
        """Test: Path is normalized during registration."""
        registry = RouterRegistry()
        def handler(req):
            return ("200 OK", "Test")

        registry.register("/users/", handler, methods=["GET"])

        assert "/users" in registry.static_routes
        assert "/users/" not in registry.static_routes


# ============================================================================
# Route Conflict Tests
# ============================================================================


@pytest.mark.unit
class TestRouteConflicts:
    """Tests for route conflict detection."""

    def test_conflict_same_path_same_method(self):
        """Test: Detect conflict for same path and method."""
        registry = RouterRegistry()
        def handler1(req):
            return ("200 OK", "Handler 1")
        def handler2(req):
            return ("200 OK", "Handler 2")

        registry.register("/users", handler1, methods=["GET"])

        with pytest.raises(RouteConflictError, match="GET /users already registered"):
            registry.register("/users", handler2, methods=["GET"])

    def test_no_conflict_same_path_different_method(self):
        """Test: No conflict for same path with different methods."""
        registry = RouterRegistry()
        def handler1(req):
            return ("200 OK", "GET")
        def handler2(req):
            return ("201 Created", "POST")

        registry.register("/users", handler1, methods=["GET"])
        registry.register("/users", handler2, methods=["POST"])

        assert "GET" in registry.static_routes["/users"]
        assert "POST" in registry.static_routes["/users"]

    def test_conflict_overlapping_methods(self):
        """Test: Detect conflict with overlapping method lists."""
        registry = RouterRegistry()
        def handler1(req):
            return ("200 OK", "Handler 1")
        def handler2(req):
            return ("200 OK", "Handler 2")

        registry.register("/users", handler1, methods=["GET", "POST"])

        with pytest.raises(RouteConflictError):
            registry.register("/users", handler2, methods=["POST", "PUT"])

    def test_conflict_dynamic_route(self):
        """Test: Detect conflict in dynamic routes."""
        registry = RouterRegistry()
        def handler1(req):
            return ("200 OK", "Handler 1")
        def handler2(req):
            return ("200 OK", "Handler 2")

        registry.register("/users/{id}", handler1, methods=["GET"])

        with pytest.raises(RouteConflictError):
            registry.register("/users/{id}", handler2, methods=["GET"])

    def test_no_conflict_different_dynamic_patterns(self):
        """Test: No conflict for different dynamic patterns."""
        registry = RouterRegistry()
        def handler1(req):
            return ("200 OK", "User")
        def handler2(req):
            return ("200 OK", "Post")

        registry.register("/users/{id}", handler1, methods=["GET"])
        registry.register("/posts/{id}", handler2, methods=["GET"])

        assert len(registry.dynamic_routes) == 2


# ============================================================================
# Route Matching Tests
# ============================================================================


@pytest.mark.unit
class TestRouteMatching:
    """Tests for route matching algorithm."""

    def test_match_static_route(self):
        """Test: Match static route with O(1) lookup."""
        registry = RouterRegistry()
        def handler(req):
            return ("200 OK", "Users")

        registry.register("/users", handler, methods=["GET"])

        matched_handler, params, allowed = registry.match("/users", "GET")

        assert matched_handler == handler
        assert params is None  # Static routes return None for params
        assert allowed is True

    def test_match_dynamic_route(self):
        """Test: Match dynamic route and extract parameters."""
        registry = RouterRegistry()
        def handler(req):
            return ("200 OK", "User")

        registry.register("/users/{id:int}", handler, methods=["GET"])

        matched_handler, params, allowed = registry.match("/users/42", "GET")

        assert matched_handler == handler
        assert params == {"id": 42}
        assert allowed is True

    def test_match_not_found(self):
        """Test: Return (None, None, None) for non-existent route."""
        registry = RouterRegistry()

        matched_handler, params, allowed = registry.match("/nonexistent", "GET")

        assert matched_handler is None
        assert params is None
        assert allowed is None

    def test_match_method_not_allowed(self):
        """Test: Return (None, None, False) for wrong HTTP method."""
        registry = RouterRegistry()
        def handler(req):
            return ("200 OK", "Users")

        registry.register("/users", handler, methods=["GET"])

        matched_handler, params, allowed = registry.match("/users", "POST")

        assert matched_handler is None
        assert params is None
        assert allowed is False

    def test_match_normalizes_path(self):
        """Test: Path normalization during matching."""
        registry = RouterRegistry()
        def handler(req):
            return ("200 OK", "Users")

        registry.register("/users", handler, methods=["GET"])

        matched_handler, _params, allowed = registry.match("/users/", "GET")

        assert matched_handler == handler
        assert allowed is True

    def test_priority_static_over_dynamic(self):
        """Test: Static routes have priority over dynamic routes."""
        registry = RouterRegistry()
        def static_handler(req):
            return ("200 OK", "Static")
        def dynamic_handler(req):
            return ("200 OK", "Dynamic")

        registry.register("/users/new", static_handler, methods=["GET"])
        registry.register("/users/{id}", dynamic_handler, methods=["GET"])

        matched_handler, params, _allowed = registry.match("/users/new", "GET")

        assert matched_handler == static_handler
        assert params is None  # Matched as static

    def test_match_multiple_dynamic_params(self):
        """Test: Match route with multiple parameters."""
        registry = RouterRegistry()
        def handler(req):
            return ("200 OK", "Post")

        registry.register("/users/{user_id:int}/posts/{post_id:int}", handler, methods=["GET"])

        matched_handler, params, _allowed = registry.match("/users/5/posts/42", "GET")

        assert matched_handler == handler
        assert params == {"user_id": 5, "post_id": 42}


# ============================================================================
# Path Normalization Tests
# ============================================================================


@pytest.mark.unit
class TestPathNormalization:
    """Tests for path normalization."""

    @pytest.mark.parametrize(("path", "expected"), [
        ("/", "/"),
        ("/users", "/users"),
        ("/users/", "/users"),
        ("users", "/users"),
        ("", "/"),
        ("///users///", "/users"),
        ("/api/v1/users/", "/api/v1/users"),
    ])
    def test_normalize_path(self, path, expected):
        """Test: Path normalization for various inputs."""
        registry = RouterRegistry()

        normalized = registry._normalize_path(path)

        assert normalized == expected

    def test_root_path_not_stripped(self):
        """Test: Root path "/" is not stripped."""
        registry = RouterRegistry()

        normalized = registry._normalize_path("/")

        assert normalized == "/"


# ============================================================================
# Registry Merging Tests
# ============================================================================


@pytest.mark.unit
class TestRegistryMerging:
    """Tests for merge_from method."""

    def test_merge_static_routes_no_prefix(self):
        """Test: Merge static routes without prefix."""
        main_registry = RouterRegistry()
        other_registry = RouterRegistry()

        def handler1(req):
            return ("200 OK", "Handler 1")
        def handler2(req):
            return ("200 OK", "Handler 2")

        main_registry.register("/main", handler1, methods=["GET"])
        other_registry.register("/other", handler2, methods=["GET"])

        main_registry.merge_from(other_registry)

        assert "/main" in main_registry.static_routes
        assert "/other" in main_registry.static_routes

    def test_merge_with_prefix(self):
        """Test: Merge routes with prefix."""
        main_registry = RouterRegistry()
        other_registry = RouterRegistry()

        def handler(req):
            return ("200 OK", "Handler")

        other_registry.register("/users", handler, methods=["GET"])

        main_registry.merge_from(other_registry, prefix="/api")

        assert "/api/users" in main_registry.static_routes

    def test_merge_dynamic_routes(self):
        """Test: Merge dynamic routes."""
        main_registry = RouterRegistry()
        other_registry = RouterRegistry()

        def handler(req):
            return ("200 OK", "Handler")

        other_registry.register("/users/{id}", handler, methods=["GET"])

        main_registry.merge_from(other_registry, prefix="/api")

        assert len(main_registry.dynamic_routes) == 1
        pattern, _methods = main_registry.dynamic_routes[0]
        assert pattern.pattern_str == "/api/users/{id}"

    def test_merge_conflict_detection(self):
        """Test: Detect conflicts during merge."""
        main_registry = RouterRegistry()
        other_registry = RouterRegistry()

        def handler1(req):
            return ("200 OK", "Handler 1")
        def handler2(req):
            return ("200 OK", "Handler 2")

        main_registry.register("/users", handler1, methods=["GET"])
        other_registry.register("/users", handler2, methods=["GET"])

        with pytest.raises(RouteConflictError):
            main_registry.merge_from(other_registry)

    def test_merge_normalizes_prefix(self):
        """Test: Prefix is normalized during merge."""
        main_registry = RouterRegistry()
        other_registry = RouterRegistry()

        def handler(req):
            return ("200 OK", "Handler")

        other_registry.register("/users", handler, methods=["GET"])

        main_registry.merge_from(other_registry, prefix="/api/")

        assert "/api/users" in main_registry.static_routes

    def test_merge_root_prefix(self):
        """Test: Merge with root prefix."""
        main_registry = RouterRegistry()
        other_registry = RouterRegistry()

        def handler(req):
            return ("200 OK", "Handler")

        other_registry.register("/users", handler, methods=["GET"])

        main_registry.merge_from(other_registry, prefix="/")

        assert "/users" in main_registry.static_routes


# ============================================================================
# Get Allowed Methods Tests
# ============================================================================


@pytest.mark.unit
class TestGetAllowedMethods:
    """Tests for get_allowed_methods method."""

    def test_get_allowed_methods_static(self):
        """Test: Get allowed methods for static route."""
        registry = RouterRegistry()
        def handler(req):
            return ("200 OK", "Test")

        registry.register("/users", handler, methods=["GET", "POST"])

        allowed = registry.get_allowed_methods("/users")

        assert allowed == {"GET", "POST"}

    def test_get_allowed_methods_dynamic(self):
        """Test: Get allowed methods for dynamic route."""
        registry = RouterRegistry()
        def handler(req):
            return ("200 OK", "Test")

        registry.register("/users/{id}", handler, methods=["GET", "PUT", "DELETE"])

        allowed = registry.get_allowed_methods("/users/42")

        assert allowed == {"GET", "PUT", "DELETE"}

    def test_get_allowed_methods_not_found(self):
        """Test: Return None for non-existent path."""
        registry = RouterRegistry()

        allowed = registry.get_allowed_methods("/nonexistent")

        assert allowed is None


# ============================================================================
# Dynamic Route Sorting Tests
# ============================================================================


@pytest.mark.unit
class TestDynamicRouteSorting:
    """Tests for dynamic route sorting by specificity."""

    def test_routes_sorted_by_segments(self):
        """Test: Routes sorted by number of segments (more specific first)."""
        registry = RouterRegistry()

        def handler1(req):
            return ("200 OK", "1")
        def handler2(req):
            return ("200 OK", "2")
        def handler3(req):
            return ("200 OK", "3")

        registry.register("/a/{id}", handler1, methods=["GET"])
        registry.register("/a/{id}/b/{id2}", handler2, methods=["GET"])
        registry.register("/a/{id}/b/{id2}/c/{id3}", handler3, methods=["GET"])

        # More segments should come first
        assert registry.dynamic_routes[0][0].segments_count > registry.dynamic_routes[1][0].segments_count
        assert registry.dynamic_routes[1][0].segments_count > registry.dynamic_routes[2][0].segments_count

    def test_matching_uses_most_specific(self):
        """Test: Matching uses most specific route first."""
        registry = RouterRegistry()

        def specific_handler(req):
            return ("200 OK", "Specific")
        def general_handler(req):
            return ("200 OK", "General")

        registry.register("/users/{id}/posts/{post_id}", specific_handler, methods=["GET"])
        registry.register("/users/{id}", general_handler, methods=["GET"])

        matched_handler, params, _allowed = registry.match("/users/1/posts/2", "GET")

        assert matched_handler == specific_handler
        assert params == {"id": "1", "post_id": "2"}
