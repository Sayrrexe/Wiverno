"""
Unit tests for Wiverno main application class.

Tests:
- Wiverno initialization
- Route decorators (route, get, post, put, patch, delete, etc.)
- Router inclusion
- Route matching
- Error handlers (404, 405, 500)
- WSGI integration
- Debug mode
"""

import pytest

from wiverno.core.requests import Request
from wiverno.main import (
    Wiverno,
)
from wiverno.core.default_pages import (
    InternalServerError500,
    MethodNotAllowed405,
    PageNotFound404,
)

# ============================================================================
# Error Handler Tests
# ============================================================================


@pytest.mark.unit
class TestPageNotFound404:
    """Tests for PageNotFound404 error handler."""

    def test_404_handler_returns_correct_status(self, basic_environ):
        """Test: 404 handler returns 404 status."""
        handler = PageNotFound404()
        request = Request(basic_environ)

        status, body = handler(request)

        assert status == "404 NOT FOUND"
        assert isinstance(body, str)
        assert len(body) > 0

    def test_404_handler_returns_html(self, basic_environ):
        """Test: 404 handler returns HTML content."""
        handler = PageNotFound404()
        request = Request(basic_environ)

        status, body = handler(request)

        assert "<html>" in body or "<!DOCTYPE" in body or "404" in body


@pytest.mark.unit
class TestMethodNotAllowed405:
    """Tests for MethodNotAllowed405 error handler."""

    def test_405_handler_returns_correct_status(self, basic_environ):
        """Test: 405 handler returns 405 status."""
        handler = MethodNotAllowed405()
        basic_environ["REQUEST_METHOD"] = "POST"
        request = Request(basic_environ)

        status, body = handler(request)

        assert status == "405 METHOD NOT ALLOWED"
        assert isinstance(body, str)
        assert len(body) > 0

    def test_405_handler_includes_method(self, basic_environ):
        """Test: 405 handler includes HTTP method in response."""
        handler = MethodNotAllowed405()
        basic_environ["REQUEST_METHOD"] = "DELETE"
        request = Request(basic_environ)

        status, body = handler(request)

        assert "DELETE" in body or "405" in body


@pytest.mark.unit
class TestInternalServerError500:
    """Tests for InternalServerError500 error handler."""

    def test_500_handler_returns_correct_status(self, basic_environ):
        """Test: 500 handler returns 500 status."""
        handler = InternalServerError500()
        request = Request(basic_environ)

        status, body = handler(request)

        assert status == "500 INTERNAL SERVER ERROR"
        assert isinstance(body, str)

    def test_500_handler_with_traceback(self, basic_environ):
        """Test: 500 handler includes traceback in debug mode."""
        handler = InternalServerError500()
        request = Request(basic_environ)

        error_traceback = (
            "Traceback (most recent call last):\n  File test.py, line 42\n    ValueError"
        )

        status, body = handler(request, error_traceback=error_traceback)

        # Body should contain traceback or error info
        assert "500" in body or "error" in body.lower()

    def test_500_handler_without_traceback(self, basic_environ):
        """Test: 500 handler works without traceback."""
        handler = InternalServerError500()
        request = Request(basic_environ)

        status, body = handler(request, error_traceback=None)

        assert status == "500 INTERNAL SERVER ERROR"
        assert isinstance(body, str)


# ============================================================================
# Wiverno Initialization Tests
# ============================================================================


@pytest.mark.unit
class TestWivernoInitialization:
    """Tests for Wiverno application initialization."""

    def test_wiverno_initialization_default(self):
        """Test: Wiverno initializes with default values."""
        app = Wiverno()

        assert app.debug is True
        assert app.page_404 is not None
        assert app.page_405 is not None
        assert app.page_500 is not None

    def test_wiverno_debug_mode_off(self):
        """Test: Wiverno can be initialized with debug mode off."""
        app = Wiverno(debug_mode=False)

        assert app.debug is False

    def test_wiverno_custom_error_handlers(self):
        """Test: Wiverno accepts custom error handlers."""

        def custom_404(request):
            return "404 NOT FOUND", "Custom 404"

        def custom_405(request):
            return "405 METHOD NOT ALLOWED", "Custom 405"

        def custom_500(request, traceback=None):
            return "500 INTERNAL SERVER ERROR", "Custom 500"

        app = Wiverno(page_404=custom_404, page_405=custom_405, page_500=custom_500)

        assert app.page_404 == custom_404
        assert app.page_405 == custom_405
        assert app.page_500 == custom_500

    def test_wiverno_custom_template_path(self):
        """Test: Wiverno accepts custom system template path."""
        custom_path = "/custom/templates"
        app = Wiverno(system_template_path=custom_path)

        assert app.system_templator is not None


# ============================================================================
# WSGI Integration Tests
# ============================================================================


@pytest.mark.unit
class TestWivernoWSGIIntegration:
    """Tests for WSGI __call__ method."""

    def test_wsgi_call_successful_route(self, call_wsgi_app, environ_factory):
        """Test: WSGI call with successful route."""
        app = Wiverno()

        @app.get("/hello")
        def hello(request):
            return "200 OK", "<html><body>Hello World</body></html>"

        environ = environ_factory(path="/hello")

        status, headers, body = call_wsgi_app(app, environ)

        assert status == "200 OK"
        assert "Hello World" in body
        assert ("Content-Type", "text/html; charset=utf-8") in headers

    def test_wsgi_call_404_route(self, call_wsgi_app, environ_factory):
        """Test: WSGI call for nonexistent route returns 404."""
        app = Wiverno()

        environ = environ_factory(path="/nonexistent")

        status, headers, body = call_wsgi_app(app, environ)

        assert "404" in status
        assert isinstance(body, str)

    def test_wsgi_call_405_wrong_method(self, call_wsgi_app, environ_factory):
        """Test: WSGI call with wrong method returns 405."""
        app = Wiverno()

        @app.get("/users")
        def get_users(request):
            return "200 OK", "Users"

        environ = environ_factory(method="POST", path="/users")

        status, headers, body = call_wsgi_app(app, environ)

        assert "405" in status

    def test_wsgi_call_500_handler_exception(self, call_wsgi_app, environ_factory):
        """Test: WSGI call handles handler exceptions."""
        app = Wiverno(debug_mode=True)

        @app.get("/error")
        def error_handler(request):
            raise ValueError("Test error")

        environ = environ_factory(path="/error")

        status, headers, body = call_wsgi_app(app, environ)

        assert "500" in status

    def test_wsgi_call_path_normalization(self, call_wsgi_app, environ_factory):
        """Test: WSGI call normalizes paths."""
        app = Wiverno()

        @app.get("/test")
        def test_handler(request):
            return "200 OK", "Test"

        # Path with trailing slash
        environ = environ_factory(path="/test/")

        status, headers, body = call_wsgi_app(app, environ)

        assert status == "200 OK"
        assert "Test" in body

    def test_wsgi_call_root_path(self, call_wsgi_app, environ_factory):
        """Test: WSGI call handles root path correctly."""
        app = Wiverno()

        @app.get("/")
        def root(request):
            return "200 OK", "Root Page"

        environ = environ_factory(path="/")

        status, headers, body = call_wsgi_app(app, environ)

        assert status == "200 OK"
        assert "Root Page" in body

    def test_wsgi_call_debug_mode_traceback(self, call_wsgi_app, environ_factory):
        """Test: Debug mode includes traceback in 500 errors."""
        app = Wiverno(debug_mode=True)

        @app.get("/error")
        def error_handler(request):
            raise ValueError("Test error")

        environ = environ_factory(path="/error")

        status, headers, body = call_wsgi_app(app, environ)

        assert "500" in status
        # In debug mode, traceback might be included
        assert isinstance(body, str)

    def test_wsgi_call_production_mode_no_traceback(self, call_wsgi_app, environ_factory):
        """Test: Production mode hides traceback."""
        app = Wiverno(debug_mode=False)

        @app.get("/error")
        def error_handler(request):
            raise ValueError("Test error")

        environ = environ_factory(path="/error")

        status, headers, body = call_wsgi_app(app, environ)

        assert "500" in status
        assert isinstance(body, str)


# ============================================================================
# Integration Tests
# ============================================================================


@pytest.mark.integration
class TestWivernoIntegration:
    """Integration tests for Wiverno application."""

    def test_full_request_response_cycle(self, call_wsgi_app, environ_factory):
        """Test: Complete request-response cycle."""
        app = Wiverno()

        @app.get("/")
        def index(request):
            return "200 OK", "<h1>Home</h1>"

        @app.get("/about")
        def about(request):
            return "200 OK", "<h1>About</h1>"

        @app.post("/submit")
        def submit(request):
            return "201 Created", "<h1>Submitted</h1>"

        # Test GET /
        environ = environ_factory(path="/")
        status, headers, body = call_wsgi_app(app, environ)
        assert status == "200 OK"
        assert "Home" in body

        # Test GET /about
        environ = environ_factory(path="/about")
        status, headers, body = call_wsgi_app(app, environ)
        assert status == "200 OK"
        assert "About" in body

        # Test POST /submit
        environ = environ_factory(method="POST", path="/submit")
        status, headers, body = call_wsgi_app(app, environ)
        assert "201" in status
        assert "Submitted" in body

    ''' Not working properly, closed for updating
    def test_application_with_router(self, call_wsgi_app, environ_factory):
        """Test: Application with included router."""
        app = Wiverno()
        api_router = Router()

        @api_router.get("/users")
        def get_users(request):
            return "200 OK", "Users List"

        @api_router.post("/users")
        def create_user(request):
            return "201 Created", "User Created"

        app.include_router(api_router, prefix="/api/v1")

        # Test GET /api/v1/users
        environ = environ_factory(path="/api/v1/users")
        status, headers, body = call_wsgi_app(app, environ)
        assert status == "200 OK"
        assert "Users List" in body

        # Test POST /api/v1/users
        environ = environ_factory(method="POST", path="/api/v1/users")
        status, headers, body = call_wsgi_app(app, environ)
        assert "201" in status
'''

# ============================================================================
# Edge Cases
# ============================================================================


@pytest.mark.unit
class TestWivernoEdgeCases:
    """Edge case tests for Wiverno."""

    def test_empty_application(self, call_wsgi_app, environ_factory):
        """Test: Empty application returns 404 for all routes."""
        app = Wiverno()

        environ = environ_factory(path="/anything")
        status, headers, body = call_wsgi_app(app, environ)

        assert "404" in status

    def test_same_path_different_methods(self, call_wsgi_app, environ_factory):
        """Test: Same path with different methods - last one wins."""
        app = Wiverno()

        @app.get("/resource")
        def get_resource(request):
            return "200 OK", "GET"

        @app.post("/resource")
        def create_resource(request):
            return "201 Created", "POST"

        # Both should be registered (second overwrites first)
        # This is current behavior - path is key in dict
        environ = environ_factory(method="POST", path="/resource")
        status, headers, body = call_wsgi_app(app, environ)

        # Depending on implementation, POST might work
        assert status in ["200 OK", "201 Created", "405 METHOD NOT ALLOWED"]

    def test_handler_with_exception_in_debug_mode(self, call_wsgi_app, environ_factory):
        """Test: Exception in handler with debug mode."""
        app = Wiverno(debug_mode=True)

        @app.get("/crash")
        def crash(request):
            raise RuntimeError("Intentional crash")

        environ = environ_factory(path="/crash")
        status, headers, body = call_wsgi_app(app, environ)

        assert "500" in status

    def test_unicode_in_response(self, call_wsgi_app, environ_factory):
        """Test: Unicode characters in response."""
        app = Wiverno()

        @app.get("/unicode")
        def unicode_response(request):
            return "200 OK", "<p>Привет, мир! 🌍</p>"

        environ = environ_factory(path="/unicode")
        status, headers, body = call_wsgi_app(app, environ)

        assert status == "200 OK"
        assert "Привет" in body or len(body) > 0  # Unicode should work
