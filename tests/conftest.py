"""
Common pytest fixtures for Wiverno tests.

This file contains reusable fixtures for unit and integration tests.
"""

import io
import tempfile
from pathlib import Path
from typing import Any

import pytest

from wiverno.core.requests import Request
from wiverno.core.router import Router
from wiverno.main import Wiverno

# ============================================================================
# WSGI Environment Fixtures
# ============================================================================


@pytest.fixture
def basic_environ() -> dict[str, Any]:
    """Basic WSGI environment for tests."""
    return {
        "REQUEST_METHOD": "GET",
        "PATH_INFO": "/",
        "QUERY_STRING": "",
        "SERVER_NAME": "testserver",
        "SERVER_PORT": "80",
        "wsgi.url_scheme": "http",
        "wsgi.input": io.BytesIO(b""),
        "CONTENT_LENGTH": "0",
        "CONTENT_TYPE": "",
    }


@pytest.fixture
def environ_factory(basic_environ):
    """Factory for creating customized WSGI environments."""

    def _make_environ(
        method: str = "GET",
        path: str = "/",
        query_string: str = "",
        body: bytes = b"",
        content_type: str = "",
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Create WSGI environment with given parameters."""
        environ = basic_environ.copy()
        environ["REQUEST_METHOD"] = method
        environ["PATH_INFO"] = path
        environ["QUERY_STRING"] = query_string
        environ["wsgi.input"] = io.BytesIO(body)
        environ["CONTENT_LENGTH"] = str(len(body))

        if content_type:
            environ["CONTENT_TYPE"] = content_type

        # Add custom headers in WSGI format
        if headers:
            for key, value in headers.items():
                wsgi_key = f"HTTP_{key.upper().replace('-', '_')}"
                environ[wsgi_key] = value

        return environ

    return _make_environ


# ============================================================================
# Router Fixtures
# ============================================================================


@pytest.fixture
def router() -> Router:
    """Clean Router instance for tests."""
    return Router()


@pytest.fixture
def router_with_routes(router: Router) -> Router:
    """Router with predefined test routes."""

    @router.get("/")
    def home(request):
        return "200 OK", "Home"

    @router.get("/users")
    def users_list(request):
        return "200 OK", "Users List"

    @router.post("/users")
    def create_user(request):
        return "200 OK", "Create User"

    @router.get("/users/<id>")
    def get_user(request, user_id):
        return "200 OK", f"User {user_id}"

    return router


# ============================================================================
# Wiverno Application Fixtures
# ============================================================================


@pytest.fixture
def app() -> Wiverno:
    """Clean Wiverno application instance."""
    return Wiverno(debug_mode=True)


@pytest.fixture
def app_with_routes() -> Wiverno:
    """Wiverno application with predefined test routes."""
    app = Wiverno(debug_mode=True)

    @app.get("/")
    def home(request):
        return "200 OK", "Home Page"

    @app.post("/api/data")
    def api_data(request):
        return "200 OK", f"Data: {request.data}"

    @app.get("/error")
    def error_route(request):
        raise ValueError("Test error")

    return app


# ============================================================================
# Request Fixtures
# ============================================================================


@pytest.fixture
def request_factory(environ_factory):
    """Factory for creating Request objects."""

    def _make_request(**kwargs) -> Request:
        """Create Request object from WSGI environment."""
        environ = environ_factory(**kwargs)
        return Request(environ)

    return _make_request


# ============================================================================
# Template and File Fixtures
# ============================================================================


@pytest.fixture
def temp_template_dir():
    """Temporary directory for test templates."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_template(temp_template_dir):
    """Create a simple test template."""
    template_content = """
    <!DOCTYPE html>
    <html>
    <head><title>{{ title }}</title></head>
    <body>
        <h1>{{ heading }}</h1>
        <p>{{ content }}</p>
    </body>
    </html>
    """
    template_file = temp_template_dir / "test.html"
    template_file.write_text(template_content.strip())
    return temp_template_dir


# ============================================================================
# Testing Utilities
# ============================================================================


@pytest.fixture
def call_wsgi_app():
    """Utility for calling WSGI application and getting response."""

    def _call(app, environ):
        """Call WSGI application and return status, headers, and body."""
        response_status = []
        response_headers = []

        def start_response(status, headers):
            response_status.append(status)
            response_headers.append(headers)

        body_iter = app(environ, start_response)
        body = b"".join(body_iter)

        return response_status[0], response_headers[0], body.decode("utf-8")

    return _call


# ============================================================================
# Pytest Configuration
# ============================================================================


def pytest_configure(config):
    """Register custom markers for pytest."""
    config.addinivalue_line("markers", "unit: Unit tests (fast, isolated)")
    config.addinivalue_line(
        "markers", "integration: Integration tests (slower, multiple components)"
    )
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "benchmark: Performance benchmark tests")
