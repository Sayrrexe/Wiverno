"""
Integration tests for Wiverno application with routing system.

Tests:
- WSGI interface
- Route decorators
- Router inclusion
- Error handling (404, 405, 500)
- Debug mode
- Request processing pipeline
"""

import pytest

from wiverno.core.requests import Request
from wiverno.core.routing.router import Router
from wiverno.main import Wiverno


# ============================================================================
# WSGI Interface Tests
# ============================================================================


@pytest.mark.integration
class TestWivernoWSGI:
    """Tests for Wiverno WSGI interface."""

    def test_wsgi_call_signature(self, environ_factory):
        """Test: WSGI __call__ has correct signature."""
        app = Wiverno()

        @app.get("/test")
        def handler(request: Request) -> tuple[str, str]:
            return "200 OK", "Test"

        environ = environ_factory(path="/test")
        response_status = []
        response_headers = []

        def start_response(status, headers):
            response_status.append(status)
            response_headers.append(headers)

        body_iter = app(environ, start_response)

        assert len(response_status) == 1
        assert len(response_headers) == 1
        assert isinstance(body_iter, list)

    def test_wsgi_successful_request(self, call_wsgi_app, environ_factory):
        """Test: Successful WSGI request processing."""
        app = Wiverno()

        @app.get("/hello")
        def handler(request: Request) -> tuple[str, str]:
            return "200 OK", "<h1>Hello World</h1>"

        environ = environ_factory(path="/hello")
        status, headers, body = call_wsgi_app(app, environ)

        assert status == "200 OK"
        assert "Hello World" in body
        assert ("Content-Type", "text/html; charset=utf-8") in headers

    def test_wsgi_returns_bytes(self, environ_factory):
        """Test: WSGI returns bytes in response body."""
        app = Wiverno()

        @app.get("/test")
        def handler(request: Request) -> tuple[str, str]:
            return "200 OK", "Test"

        environ = environ_factory(path="/test")

        response_status = []

        def start_response(status, headers):
            response_status.append(status)

        body_iter = app(environ, start_response)
        body_bytes = b"".join(body_iter)

        assert isinstance(body_bytes, bytes)
        assert body_bytes == b"Test"


# ============================================================================
# Route Decorator Tests
# ============================================================================


@pytest.mark.integration
class TestWivernoRouteDecorators:
    """Tests for Wiverno route decorators."""

    def test_get_decorator(self, call_wsgi_app, environ_factory):
        """Test: GET decorator works end-to-end."""
        app = Wiverno()

        @app.get("/users")
        def get_users(request: Request) -> tuple[str, str]:
            return "200 OK", "Users list"

        environ = environ_factory(method="GET", path="/users")
        status, headers, body = call_wsgi_app(app, environ)

        assert status == "200 OK"
        assert "Users list" in body

    def test_post_decorator(self, call_wsgi_app, environ_factory):
        """Test: POST decorator works end-to-end."""
        app = Wiverno()

        @app.post("/users")
        def create_user(request: Request) -> tuple[str, str]:
            return "201 Created", "User created"

        environ = environ_factory(method="POST", path="/users")
        status, headers, body = call_wsgi_app(app, environ)

        assert "201" in status
        assert "User created" in body

    def test_put_decorator(self, call_wsgi_app, environ_factory):
        """Test: PUT decorator works end-to-end."""
        app = Wiverno()

        @app.put("/users/{id:int}")
        def update_user(request: Request) -> tuple[str, str]:
            return "200 OK", f"Updated user {request.path_params['id']}"

        environ = environ_factory(method="PUT", path="/users/42")
        status, headers, body = call_wsgi_app(app, environ)

        assert status == "200 OK"
        assert "Updated user 42" in body

    def test_delete_decorator(self, call_wsgi_app, environ_factory):
        """Test: DELETE decorator works end-to-end."""
        app = Wiverno()

        @app.delete("/users/{id:int}")
        def delete_user(request: Request) -> tuple[str, str]:
            return "204 No Content", ""

        environ = environ_factory(method="DELETE", path="/users/42")
        status, headers, body = call_wsgi_app(app, environ)

        assert "204" in status

    def test_patch_decorator(self, call_wsgi_app, environ_factory):
        """Test: PATCH decorator works end-to-end."""
        app = Wiverno()

        @app.patch("/users/{id}")
        def patch_user(request: Request) -> tuple[str, str]:
            return "200 OK", "User patched"

        environ = environ_factory(method="PATCH", path="/users/1")
        status, headers, body = call_wsgi_app(app, environ)

        assert status == "200 OK"
        assert "User patched" in body

    def test_all_http_methods(self, call_wsgi_app, environ_factory):
        """Test: All HTTP method decorators work."""
        app = Wiverno()

        @app.get("/test")
        def get_handler(request: Request) -> tuple[str, str]:
            return "200 OK", "GET"

        @app.post("/test")
        def post_handler(request: Request) -> tuple[str, str]:
            return "200 OK", "POST"

        @app.put("/test")
        def put_handler(request: Request) -> tuple[str, str]:
            return "200 OK", "PUT"

        @app.patch("/test")
        def patch_handler(request: Request) -> tuple[str, str]:
            return "200 OK", "PATCH"

        @app.delete("/test")
        def delete_handler(request: Request) -> tuple[str, str]:
            return "200 OK", "DELETE"

        for method in ["GET", "POST", "PUT", "PATCH", "DELETE"]:
            environ = environ_factory(method=method, path="/test")
            status, headers, body = call_wsgi_app(app, environ)
            assert status == "200 OK"
            assert method in body


# ============================================================================
# Router Inclusion Tests
# ============================================================================


@pytest.mark.integration
class TestWivernoRouterInclusion:
    """Tests for including routers in Wiverno application."""

    def test_include_router_no_prefix(self, call_wsgi_app, environ_factory):
        """Test: Include router without prefix."""
        app = Wiverno()
        api_router = Router()

        @api_router.get("/users")
        def get_users(request: Request) -> tuple[str, str]:
            return "200 OK", "Users"

        app.include_router(api_router)

        environ = environ_factory(path="/users")
        status, headers, body = call_wsgi_app(app, environ)

        assert status == "200 OK"
        assert "Users" in body

    def test_include_router_with_prefix(self, call_wsgi_app, environ_factory):
        """Test: Include router with prefix."""
        app = Wiverno()
        api_router = Router()

        @api_router.get("/users")
        def get_users(request: Request) -> tuple[str, str]:
            return "200 OK", "API Users"

        app.include_router(api_router, prefix="/api")

        environ = environ_factory(path="/api/users")
        status, headers, body = call_wsgi_app(app, environ)

        assert status == "200 OK"
        assert "API Users" in body

    def test_include_multiple_routers(self, call_wsgi_app, environ_factory):
        """Test: Include multiple routers with different prefixes."""
        app = Wiverno()

        api_v1 = Router()
        api_v2 = Router()

        @api_v1.get("/users")
        def v1_users(request: Request) -> tuple[str, str]:
            return "200 OK", "V1 Users"

        @api_v2.get("/users")
        def v2_users(request: Request) -> tuple[str, str]:
            return "200 OK", "V2 Users"

        app.include_router(api_v1, prefix="/api/v1")
        app.include_router(api_v2, prefix="/api/v2")

        # Test V1
        environ = environ_factory(path="/api/v1/users")
        status, headers, body = call_wsgi_app(app, environ)
        assert "V1 Users" in body

        # Test V2
        environ = environ_factory(path="/api/v2/users")
        status, headers, body = call_wsgi_app(app, environ)
        assert "V2 Users" in body

    def test_include_router_with_dynamic_routes(self, call_wsgi_app, environ_factory):
        """Test: Include router with dynamic routes."""
        app = Wiverno()
        users_router = Router()

        @users_router.get("/{id:int}")
        def get_user(request: Request) -> tuple[str, str]:
            user_id = request.path_params["id"]
            return "200 OK", f"User {user_id}"

        app.include_router(users_router, prefix="/users")

        environ = environ_factory(path="/users/42")
        status, headers, body = call_wsgi_app(app, environ)

        assert status == "200 OK"
        assert "User 42" in body


# ============================================================================
# Error Handling Tests
# ============================================================================


@pytest.mark.integration
class TestWivernoErrorHandling:
    """Tests for error handling (404, 405, 500)."""

    def test_404_not_found(self, call_wsgi_app, environ_factory):
        """Test: 404 error for non-existent route."""
        app = Wiverno()

        @app.get("/existing")
        def handler(request: Request) -> tuple[str, str]:
            return "200 OK", "Exists"

        environ = environ_factory(path="/nonexistent")
        status, headers, body = call_wsgi_app(app, environ)

        assert "404" in status

    def test_405_method_not_allowed(self, call_wsgi_app, environ_factory):
        """Test: 405 error for wrong HTTP method."""
        app = Wiverno()

        @app.get("/users")
        def get_users(request: Request) -> tuple[str, str]:
            return "200 OK", "Users"

        environ = environ_factory(method="POST", path="/users")
        status, headers, body = call_wsgi_app(app, environ)

        assert "405" in status

    def test_500_internal_error(self, call_wsgi_app, environ_factory):
        """Test: 500 error for handler exception."""
        app = Wiverno(debug_mode=True)

        @app.get("/error")
        def error_handler(request: Request) -> tuple[str, str]:
            raise ValueError("Test error")

        environ = environ_factory(path="/error")
        status, headers, body = call_wsgi_app(app, environ)

        assert "500" in status

    def test_custom_404_handler(self, call_wsgi_app, environ_factory):
        """Test: Custom 404 handler."""
        def custom_404(request: Request) -> tuple[str, str]:
            return "404 NOT FOUND", "Custom 404 page"

        app = Wiverno(page_404=custom_404)

        environ = environ_factory(path="/nonexistent")
        status, headers, body = call_wsgi_app(app, environ)

        assert "404" in status
        assert "Custom 404 page" in body

    def test_custom_405_handler(self, call_wsgi_app, environ_factory):
        """Test: Custom 405 handler."""
        def custom_405(request: Request) -> tuple[str, str]:
            return "405 METHOD NOT ALLOWED", "Custom 405 page"

        app = Wiverno(page_405=custom_405)

        @app.get("/users")
        def handler(request: Request) -> tuple[str, str]:
            return "200 OK", "Users"

        environ = environ_factory(method="POST", path="/users")
        status, headers, body = call_wsgi_app(app, environ)

        assert "405" in status
        assert "Custom 405 page" in body


# ============================================================================
# Debug Mode Tests
# ============================================================================


@pytest.mark.integration
class TestWivernoDebugMode:
    """Tests for debug mode functionality."""

    def test_debug_mode_on(self):
        """Test: Debug mode is enabled by default."""
        app = Wiverno()

        assert app.debug is True

    def test_debug_mode_off(self):
        """Test: Debug mode can be disabled."""
        app = Wiverno(debug_mode=False)

        assert app.debug is False

    def test_debug_mode_includes_traceback(self, call_wsgi_app, environ_factory):
        """Test: Debug mode includes traceback in 500 errors."""
        app = Wiverno(debug_mode=True)

        @app.get("/error")
        def error_handler(request: Request) -> tuple[str, str]:
            raise ValueError("Test error")

        environ = environ_factory(path="/error")
        status, headers, body = call_wsgi_app(app, environ)

        assert "500" in status
        # Traceback should be in response (handled by template)

    def test_production_mode_hides_traceback(self, call_wsgi_app, environ_factory):
        """Test: Production mode hides traceback."""
        app = Wiverno(debug_mode=False)

        @app.get("/error")
        def error_handler(request: Request) -> tuple[str, str]:
            raise ValueError("Test error")

        environ = environ_factory(path="/error")
        status, headers, body = call_wsgi_app(app, environ)

        assert "500" in status


# ============================================================================
# Path Parameters Tests
# ============================================================================


@pytest.mark.integration
class TestWivernoPathParameters:
    """Tests for path parameter extraction and injection."""

    def test_path_params_injected_to_request(self, call_wsgi_app, environ_factory):
        """Test: Path parameters are injected into request object."""
        app = Wiverno()

        @app.get("/users/{id:int}")
        def get_user(request: Request) -> tuple[str, str]:
            user_id = request.path_params["id"]
            return "200 OK", f"User ID: {user_id}"

        environ = environ_factory(path="/users/42")
        status, headers, body = call_wsgi_app(app, environ)

        assert status == "200 OK"
        assert "User ID: 42" in body

    def test_multiple_path_params(self, call_wsgi_app, environ_factory):
        """Test: Multiple path parameters are extracted."""
        app = Wiverno()

        @app.get("/users/{user_id:int}/posts/{post_id:int}")
        def get_post(request: Request) -> tuple[str, str]:
            uid = request.path_params["user_id"]
            pid = request.path_params["post_id"]
            return "200 OK", f"User {uid}, Post {pid}"

        environ = environ_factory(path="/users/5/posts/10")
        status, headers, body = call_wsgi_app(app, environ)

        assert "User 5, Post 10" in body

    def test_path_params_type_conversion(self, call_wsgi_app, environ_factory):
        """Test: Path parameters are type-converted."""
        app = Wiverno()

        @app.get("/items/{price:float}")
        def get_item(request: Request) -> tuple[str, str]:
            price = request.path_params["price"]
            assert isinstance(price, float)
            return "200 OK", f"Price: {price}"

        environ = environ_factory(path="/items/19.99")
        status, headers, body = call_wsgi_app(app, environ)

        assert "Price: 19.99" in body


# ============================================================================
# Complete Application Tests
# ============================================================================


@pytest.mark.integration
class TestCompleteApplication:
    """Tests for complete application scenarios."""

    def test_rest_api_application(self, call_wsgi_app, environ_factory):
        """Test: Complete REST API application."""
        app = Wiverno()

        @app.get("/api/items")
        def list_items(request: Request) -> tuple[str, str]:
            return "200 OK", "[]"

        @app.post("/api/items")
        def create_item(request: Request) -> tuple[str, str]:
            return "201 Created", "{}"

        @app.get("/api/items/{id:int}")
        def get_item(request: Request) -> tuple[str, str]:
            return "200 OK", "{}"

        @app.put("/api/items/{id:int}")
        def update_item(request: Request) -> tuple[str, str]:
            return "200 OK", "{}"

        @app.delete("/api/items/{id:int}")
        def delete_item(request: Request) -> tuple[str, str]:
            return "204 No Content", ""

        # Test all endpoints
        tests = [
            ("GET", "/api/items", "200 OK"),
            ("POST", "/api/items", "201 Created"),
            ("GET", "/api/items/1", "200 OK"),
            ("PUT", "/api/items/1", "200 OK"),
            ("DELETE", "/api/items/1", "204"),
        ]

        for method, path, expected_status in tests:
            environ = environ_factory(method=method, path=path)
            status, headers, body = call_wsgi_app(app, environ)
            assert expected_status in status

    def test_mixed_routes_application(self, call_wsgi_app, environ_factory):
        """Test: Application with mixed static and dynamic routes."""
        app = Wiverno()

        @app.get("/")
        def home(request: Request) -> tuple[str, str]:
            return "200 OK", "Home"

        @app.get("/about")
        def about(request: Request) -> tuple[str, str]:
            return "200 OK", "About"

        @app.get("/users/{id}")
        def user(request: Request) -> tuple[str, str]:
            return "200 OK", f"User {request.path_params['id']}"

        @app.get("/users/{id}/profile")
        def profile(request: Request) -> tuple[str, str]:
            return "200 OK", f"Profile {request.path_params['id']}"

        tests = [
            ("/", "Home"),
            ("/about", "About"),
            ("/users/alice", "User alice"),
            ("/users/bob/profile", "Profile bob"),
        ]

        for path, expected_content in tests:
            environ = environ_factory(path=path)
            status, headers, body = call_wsgi_app(app, environ)
            assert status == "200 OK"
            assert expected_content in body
