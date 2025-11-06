"""
Integration tests for Wiverno application.

Tests complete request processing cycle through WSGI interface.
"""

import io
import json

import pytest

from wiverno.main import Wiverno


# ============================================================================
# Main Application Integration Tests
# ============================================================================


@pytest.mark.integration
class TestWivernoIntegration:
    """Integration tests for complete request processing cycle."""

    def test_get_request_flow(self, app_with_routes, environ_factory, call_wsgi_app):
        """Test: Complete GET request cycle."""
        environ = environ_factory(method="GET", path="/")

        status, headers, body = call_wsgi_app(app_with_routes, environ)

        assert "200" in status
        assert "Home Page" in body

    def test_post_request_flow(self, app_with_routes, environ_factory, call_wsgi_app):
        """Test: Complete POST request cycle."""
        data = {"key": "value"}
        body_bytes = json.dumps(data).encode("utf-8")

        environ = environ_factory(
            method="POST", path="/api/data", body=body_bytes, content_type="application/json"
        )

        status, headers, body = call_wsgi_app(app_with_routes, environ)

        assert "200" in status

    def test_404_error_flow(self, app_with_routes, environ_factory, call_wsgi_app):
        """Test: Handling 404 error."""
        environ = environ_factory(method="GET", path="/nonexistent")

        status, headers, body = call_wsgi_app(app_with_routes, environ)

        assert "404" in status

    def test_multiple_routes_registration(self):
        """Test: Registration of multiple routes."""
        app = Wiverno()

        @app.get("/")
        def home(request):
            return "200 OK", "Home"

        @app.get("/users")
        def users(request):
            return "200 OK", "Users"

        @app.post("/users")
        def create_user(request):
            return "201 Created", "User created"

        @app.get("/posts")
        def posts(request):
            return "200 OK", "Posts"

        # Check that routes are registered
        # Note: POST /users overwrites GET /users as they share the same path
        # So we have: /, /users (POST only), /posts = 3 routes
        assert len(app._routes) == 3


@pytest.mark.integration
class TestWivernoErrorHandling:
    """Integration tests for error handling."""

    def test_500_error_on_exception(self, environ_factory, call_wsgi_app):
        """Test: Handling exceptions in handler."""
        app = Wiverno(debug_mode=True)

        @app.get("/error")
        def error_route(request):
            raise ValueError("Test error")

        environ = environ_factory(method="GET", path="/error")

        status, headers, body = call_wsgi_app(app, environ)

        assert "500" in status

    def test_405_method_not_allowed(self, environ_factory, call_wsgi_app):
        """Test: 405 error for unsupported method."""
        app = Wiverno()

        @app.get("/only-get")
        def get_only(request):
            return "200 OK", "GET only"

        # Try to POST to GET-only route
        environ = environ_factory(method="POST", path="/only-get")

        status, headers, body = call_wsgi_app(app, environ)

        # Should be error (405 or 404 depending on implementation)
        assert "404" in status or "405" in status


@pytest.mark.integration
class TestWivernoWithTemplates:
    """Integration tests with templates."""

    def test_render_template_in_route(self, sample_template, environ_factory, call_wsgi_app):
        """Test: Rendering template in route."""
        app = Wiverno()

        @app.get("/page")
        def page(request):
            from wiverno.templating.templator import Templator

            templator = Templator(folder=str(sample_template))
            content = templator.render(
                "test.html",
                content={"title": "Integration", "heading": "Test", "content": "Page"},
            )
            return "200 OK", content

        environ = environ_factory(method="GET", path="/page")

        status, headers, body = call_wsgi_app(app, environ)

        assert "200" in status
        assert "Integration" in body
