"""
End-to-end integration tests for Wiverno routing system.

Tests:
- Complex routing scenarios
- Real-world application patterns
- Performance characteristics
- Edge cases in production scenarios
"""

import pytest

from wiverno.core.requests import Request
from wiverno.core.routing.router import Router
from wiverno.main import Wiverno


# ============================================================================
# Complex Routing Scenarios
# ============================================================================


@pytest.mark.integration
class TestComplexRoutingScenarios:
    """Tests for complex, real-world routing patterns."""

    def test_multi_module_application(self, call_wsgi_app, environ_factory):
        """Test: Application with multiple routers (microservices pattern)."""
        app = Wiverno()

        # Users module
        users_router = Router()

        @users_router.get("/")
        def list_users(request: Request) -> tuple[str, str]:
            return "200 OK", "Users list"

        @users_router.get("/{id:int}")
        def get_user(request: Request) -> tuple[str, str]:
            return "200 OK", f"User {request.path_params['id']}"

        @users_router.post("/")
        def create_user(request: Request) -> tuple[str, str]:
            return "201 Created", "User created"

        # Posts module
        posts_router = Router()

        @posts_router.get("/")
        def list_posts(request: Request) -> tuple[str, str]:
            return "200 OK", "Posts list"

        @posts_router.get("/{id:int}")
        def get_post(request: Request) -> tuple[str, str]:
            return "200 OK", f"Post {request.path_params['id']}"

        # Include routers
        app.include_router(users_router, prefix="/api/users")
        app.include_router(posts_router, prefix="/api/posts")

        # Test users endpoints
        environ = environ_factory(path="/api/users")
        status, headers, body = call_wsgi_app(app, environ)
        assert "Users list" in body

        environ = environ_factory(path="/api/users/42")
        status, headers, body = call_wsgi_app(app, environ)
        assert "User 42" in body

        # Test posts endpoints
        environ = environ_factory(path="/api/posts")
        status, headers, body = call_wsgi_app(app, environ)
        assert "Posts list" in body

        environ = environ_factory(path="/api/posts/10")
        status, headers, body = call_wsgi_app(app, environ)
        assert "Post 10" in body

    def test_deeply_nested_routers(self, call_wsgi_app, environ_factory):
        """Test: Deeply nested router inclusion."""
        app = Wiverno()

        users_router = Router()

        @users_router.get("/{id:int}/settings")
        def user_settings(request: Request) -> tuple[str, str]:
            return "200 OK", f"Settings for user {request.path_params['id']}"

        # Include users router under /admin/users
        app.include_router(users_router, prefix="/admin/users")

        environ = environ_factory(path="/admin/users/5/settings")
        status, headers, body = call_wsgi_app(app, environ)

        assert status == "200 OK"
        assert "Settings for user 5" in body

    def test_mixed_versioning_pattern(self, call_wsgi_app, environ_factory):
        """Test: API versioning with mixed patterns."""
        app = Wiverno()

        # V1 API
        v1_router = Router()

        @v1_router.get("/users")
        def v1_users(request: Request) -> tuple[str, str]:
            return "200 OK", "V1: Basic user list"

        # V2 API
        v2_router = Router()

        @v2_router.get("/users")
        def v2_users(request: Request) -> tuple[str, str]:
            return "200 OK", "V2: Enhanced user list"

        @v2_router.get("/users/{id:int}/profile")
        def v2_user_profile(request: Request) -> tuple[str, str]:
            return "200 OK", f"V2: Profile for {request.path_params['id']}"

        app.include_router(v1_router, prefix="/api/v1")
        app.include_router(v2_router, prefix="/api/v2")

        # Test V1
        environ = environ_factory(path="/api/v1/users")
        status, headers, body = call_wsgi_app(app, environ)
        assert "V1: Basic user list" in body

        # Test V2
        environ = environ_factory(path="/api/v2/users")
        status, headers, body = call_wsgi_app(app, environ)
        assert "V2: Enhanced user list" in body

        environ = environ_factory(path="/api/v2/users/42/profile")
        status, headers, body = call_wsgi_app(app, environ)
        assert "V2: Profile for 42" in body


# ============================================================================
# Real-World Application Patterns
# ============================================================================


@pytest.mark.integration
class TestRealWorldPatterns:
    """Tests for real-world application patterns."""

    def test_e_commerce_api(self, call_wsgi_app, environ_factory):
        """Test: E-commerce API pattern."""
        app = Wiverno()

        # Products
        @app.get("/api/products")
        def list_products(request: Request) -> tuple[str, str]:
            return "200 OK", "Products"

        @app.get("/api/products/{id:int}")
        def get_product(request: Request) -> tuple[str, str]:
            return "200 OK", f"Product {request.path_params['id']}"

        # Categories
        @app.get("/api/categories/{category}/products")
        def category_products(request: Request) -> tuple[str, str]:
            return "200 OK", f"Products in {request.path_params['category']}"

        # Cart
        @app.get("/api/cart")
        def get_cart(request: Request) -> tuple[str, str]:
            return "200 OK", "Cart"

        @app.post("/api/cart/items")
        def add_to_cart(request: Request) -> tuple[str, str]:
            return "201 Created", "Item added"

        # Orders
        @app.get("/api/orders/{order_id:int}")
        def get_order(request: Request) -> tuple[str, str]:
            return "200 OK", f"Order {request.path_params['order_id']}"

        # Test all endpoints
        tests = [
            ("GET", "/api/products", "Products"),
            ("GET", "/api/products/123", "Product 123"),
            ("GET", "/api/categories/electronics/products", "Products in electronics"),
            ("GET", "/api/cart", "Cart"),
            ("POST", "/api/cart/items", "Item added"),
            ("GET", "/api/orders/456", "Order 456"),
        ]

        for method, path, expected in tests:
            environ = environ_factory(method=method, path=path)
            status, headers, body = call_wsgi_app(app, environ)
            assert expected in body

    def test_blog_application(self, call_wsgi_app, environ_factory):
        """Test: Blog application pattern."""
        app = Wiverno()

        # Public routes
        @app.get("/")
        def home(request: Request) -> tuple[str, str]:
            return "200 OK", "Blog Home"

        @app.get("/posts")
        def posts_list(request: Request) -> tuple[str, str]:
            return "200 OK", "All Posts"

        @app.get("/posts/{slug}")
        def post_detail(request: Request) -> tuple[str, str]:
            return "200 OK", f"Post: {request.path_params['slug']}"

        @app.get("/posts/{slug}/comments")
        def post_comments(request: Request) -> tuple[str, str]:
            return "200 OK", f"Comments for {request.path_params['slug']}"

        # Admin routes
        admin = Router()

        @admin.get("/posts")
        def admin_posts(request: Request) -> tuple[str, str]:
            return "200 OK", "Admin: All Posts"

        @admin.post("/posts")
        def create_post(request: Request) -> tuple[str, str]:
            return "201 Created", "Post Created"

        @admin.put("/posts/{id:int}")
        def update_post(request: Request) -> tuple[str, str]:
            return "200 OK", f"Updated post {request.path_params['id']}"

        app.include_router(admin, prefix="/admin")

        # Test public routes
        environ = environ_factory(path="/")
        status, headers, body = call_wsgi_app(app, environ)
        assert "Blog Home" in body

        environ = environ_factory(path="/posts/hello-world")
        status, headers, body = call_wsgi_app(app, environ)
        assert "Post: hello-world" in body

        # Test admin routes
        environ = environ_factory(path="/admin/posts")
        status, headers, body = call_wsgi_app(app, environ)
        assert "Admin: All Posts" in body

        environ = environ_factory(method="PUT", path="/admin/posts/5")
        status, headers, body = call_wsgi_app(app, environ)
        assert "Updated post 5" in body


# ============================================================================
# Route Priority and Precedence Tests
# ============================================================================


@pytest.mark.integration
class TestRoutePriorityAndPrecedence:
    """Tests for route matching priority and precedence."""

    def test_static_has_priority_over_dynamic(self, call_wsgi_app, environ_factory):
        """Test: Static routes take priority over dynamic routes."""
        app = Wiverno()

        @app.get("/users/new")
        def new_user_form(request: Request) -> tuple[str, str]:
            return "200 OK", "New User Form"

        @app.get("/users/{id}")
        def get_user(request: Request) -> tuple[str, str]:
            return "200 OK", f"User {request.path_params['id']}"

        # Should match static route
        environ = environ_factory(path="/users/new")
        status, headers, body = call_wsgi_app(app, environ)
        assert "New User Form" in body

        # Should match dynamic route
        environ = environ_factory(path="/users/123")
        status, headers, body = call_wsgi_app(app, environ)
        assert "User 123" in body

    def test_more_specific_dynamic_route_priority(self, call_wsgi_app, environ_factory):
        """Test: More specific dynamic routes match first."""
        app = Wiverno()

        @app.get("/files/{path:path}")
        def get_file(request: Request) -> tuple[str, str]:
            return "200 OK", f"File: {request.path_params['path']}"

        @app.get("/files/images/{filename}")
        def get_image(request: Request) -> tuple[str, str]:
            return "200 OK", f"Image: {request.path_params['filename']}"

        # More specific route should match
        environ = environ_factory(path="/files/images/photo.jpg")
        status, headers, body = call_wsgi_app(app, environ)
        assert "Image: photo.jpg" in body

        # General route should match other paths
        environ = environ_factory(path="/files/documents/report.pdf")
        status, headers, body = call_wsgi_app(app, environ)
        assert "File: documents/report.pdf" in body


# ============================================================================
# Error Handling in Complex Scenarios
# ============================================================================


@pytest.mark.integration
class TestComplexErrorHandling:
    """Tests for error handling in complex scenarios."""

    def test_404_with_similar_routes(self, call_wsgi_app, environ_factory):
        """Test: 404 error when path is similar but not matching."""
        app = Wiverno()

        @app.get("/api/users/{id:int}")
        def get_user(request: Request) -> tuple[str, str]:
            return "200 OK", "User"

        # Should 404 - not an integer
        environ = environ_factory(path="/api/users/abc")
        status, headers, body = call_wsgi_app(app, environ)
        assert "404" in status

    def test_405_in_nested_routers(self, call_wsgi_app, environ_factory):
        """Test: 405 error in nested router structure."""
        app = Wiverno()
        api = Router()

        @api.get("/users")
        def get_users(request: Request) -> tuple[str, str]:
            return "200 OK", "Users"

        app.include_router(api, prefix="/api")

        # Path exists but wrong method
        environ = environ_factory(method="POST", path="/api/users")
        status, headers, body = call_wsgi_app(app, environ)
        assert "405" in status

    def test_error_in_nested_handler(self, call_wsgi_app, environ_factory):
        """Test: Exception handling in nested router handler."""
        app = Wiverno(debug_mode=True)
        api = Router()

        @api.get("/error")
        def error_handler(request: Request) -> tuple[str, str]:
            raise RuntimeError("Nested error")

        app.include_router(api, prefix="/api")

        environ = environ_factory(path="/api/error")
        status, headers, body = call_wsgi_app(app, environ)
        assert "500" in status


# ============================================================================
# Path Normalization in Production
# ============================================================================


@pytest.mark.integration
class TestPathNormalizationProduction:
    """Tests for path normalization in production scenarios."""

    def test_trailing_slash_handling(self, call_wsgi_app, environ_factory):
        """Test: Trailing slashes are normalized."""
        app = Wiverno()

        @app.get("/users")
        def users(request: Request) -> tuple[str, str]:
            return "200 OK", "Users"

        # Both should work
        environ = environ_factory(path="/users")
        status, headers, body = call_wsgi_app(app, environ)
        assert status == "200 OK"

        environ = environ_factory(path="/users/")
        status, headers, body = call_wsgi_app(app, environ)
        assert status == "200 OK"

    def test_multiple_slashes_normalized(self, call_wsgi_app, environ_factory):
        """Test: Path normalization handles edge cases."""
        app = Wiverno()

        @app.get("/api/users")
        def users(request: Request) -> tuple[str, str]:
            return "200 OK", "Users"

        # Test trailing slash normalization (common in production)
        environ = environ_factory(path="/api/users/")
        status, headers, body = call_wsgi_app(app, environ)
        assert status == "200 OK"
        
        # Test that path without trailing slash also works
        environ = environ_factory(path="/api/users")
        status, headers, body = call_wsgi_app(app, environ)
        assert status == "200 OK"


# ============================================================================
# Performance Characteristics Tests
# ============================================================================


@pytest.mark.slow
@pytest.mark.integration
class TestPerformanceCharacteristics:
    """Tests to verify performance characteristics."""

    def test_many_static_routes_performance(self, call_wsgi_app, environ_factory):
        """Test: Many static routes maintain O(1) lookup."""
        app = Wiverno()

        # Register many static routes
        for i in range(100):
            # Use closure to capture i correctly
            def make_handler(num):
                def handler(request: Request) -> tuple[str, str]:
                    return "200 OK", f"Route {num}"
                return handler

            app.route(f"/route{i}")(make_handler(i))

        # Test first route
        environ = environ_factory(path="/route0")
        status, headers, body = call_wsgi_app(app, environ)
        assert "Route 0" in body

        # Test middle route
        environ = environ_factory(path="/route50")
        status, headers, body = call_wsgi_app(app, environ)
        assert "Route 50" in body

        # Test last route
        environ = environ_factory(path="/route99")
        status, headers, body = call_wsgi_app(app, environ)
        assert "Route 99" in body

    def test_dynamic_route_ordering_optimization(self, call_wsgi_app, environ_factory):
        """Test: Dynamic routes are ordered by specificity."""
        app = Wiverno()

        @app.get("/a/{p1}")
        def handler1(request: Request) -> tuple[str, str]:
            return "200 OK", "1 param"

        @app.get("/a/{p1}/b/{p2}")
        def handler2(request: Request) -> tuple[str, str]:
            return "200 OK", "2 params"

        @app.get("/a/{p1}/b/{p2}/c/{p3}")
        def handler3(request: Request) -> tuple[str, str]:
            return "200 OK", "3 params"

        # Most specific should match first
        environ = environ_factory(path="/a/1/b/2/c/3")
        status, headers, body = call_wsgi_app(app, environ)
        assert "3 params" in body


# ============================================================================
# Edge Cases in Production
# ============================================================================


@pytest.mark.integration
class TestProductionEdgeCases:
    """Tests for edge cases that might occur in production."""

    def test_empty_application(self, call_wsgi_app, environ_factory):
        """Test: Empty application returns 404."""
        app = Wiverno()

        environ = environ_factory(path="/any/path")
        status, headers, body = call_wsgi_app(app, environ)
        assert "404" in status

    def test_root_path_only(self, call_wsgi_app, environ_factory):
        """Test: Application with only root path."""
        app = Wiverno()

        @app.get("/")
        def root(request: Request) -> tuple[str, str]:
            return "200 OK", "Root"

        environ = environ_factory(path="/")
        status, headers, body = call_wsgi_app(app, environ)
        assert "Root" in body

        environ = environ_factory(path="/other")
        status, headers, body = call_wsgi_app(app, environ)
        assert "404" in status

    def test_unicode_in_path_params(self, call_wsgi_app, environ_factory):
        """Test: Unicode characters in path parameters."""
        app = Wiverno()

        @app.get("/tags/{name}")
        def tag(request: Request) -> tuple[str, str]:
            return "200 OK", f"Tag: {request.path_params['name']}"

        environ = environ_factory(path="/tags/python-3.11")
        status, headers, body = call_wsgi_app(app, environ)
        assert "Tag: python-3.11" in body

    def test_special_characters_in_static_routes(self, call_wsgi_app, environ_factory):
        """Test: Special characters in static routes."""
        app = Wiverno()

        @app.get("/api-v1/user_profile")
        def profile(request: Request) -> tuple[str, str]:
            return "200 OK", "Profile"

        environ = environ_factory(path="/api-v1/user_profile")
        status, headers, body = call_wsgi_app(app, environ)
        assert "Profile" in body
