"""
Integration tests for HTTP status validation in Wiverno application.

Tests ensure that HTTPStatusValidator integrates properly with the main
application flow and handles various status code scenarios correctly.
"""

import io

import pytest

from wiverno import Wiverno


def make_environ(method="GET", path="/", query="", content=""):
    """Helper function to create WSGI environ dict."""
    content_bytes = content.encode("utf-8") if isinstance(content, str) else content
    return {
        "REQUEST_METHOD": method,
        "PATH_INFO": path,
        "QUERY_STRING": query,
        "wsgi.input": io.BytesIO(content_bytes),
        "CONTENT_LENGTH": str(len(content_bytes)),
        "CONTENT_TYPE": "",
    }


class TestHTTPStatusValidationIntegration:
    """Integration tests for HTTP status validation in application context."""

    def test_handler_returns_int_status(self):
        """Test that handler can return integer status code."""
        app = Wiverno(debug_mode=False)

        @app.get("/test")
        def handler(request):
            return 201, "<h1>Created</h1>"

        status_line = None

        def start_response(status, headers):
            nonlocal status_line
            status_line = status

        app(make_environ(path="/test"), start_response)
        assert status_line == "201 Created"

    def test_handler_returns_string_status_code_only(self):
        """Test that handler can return string status code."""
        app = Wiverno(debug_mode=False)

        @app.post("/resource")
        def handler(request):
            return "204", ""

        status_line = None

        def start_response(status, headers):
            nonlocal status_line
            status_line = status

        app(make_environ(method="POST", path="/resource"), start_response)
        assert status_line == "204 No Content"

    def test_handler_returns_full_status_string(self):
        """Test that handler can return full status string."""
        app = Wiverno(debug_mode=False)

        @app.get("/redirect")
        def handler(request):
            return "301 Moved Permanently", "<h1>Moved</h1>"

        status_line = None

        def start_response(status, headers):
            nonlocal status_line
            status_line = status

        app(make_environ(path="/redirect"), start_response)
        assert status_line == "301 Moved Permanently"

    def test_handler_returns_wrong_phrase_gets_corrected(self):
        """Test that incorrect reason phrases are corrected."""
        app = Wiverno(debug_mode=False)

        @app.get("/test")
        def handler(request):
            return "404 Missing", "<h1>Not here</h1>"

        status_line = None

        def start_response(status, headers):
            nonlocal status_line
            status_line = status

        app(make_environ(path="/test"), start_response)
        assert status_line == "404 Not Found"

    def test_handler_returns_only_body_defaults_to_200(self):
        """Test that handler returning only body gets 200 OK status."""
        app = Wiverno(debug_mode=False)

        @app.get("/test")
        def handler(request):
            return "<h1>Success</h1>"

        status_line = None

        def start_response(status, headers):
            nonlocal status_line
            status_line = status

        app(make_environ(path="/test"), start_response)
        assert status_line == "200 OK"

    def test_various_success_codes(self):
        """Test various 2xx success status codes."""
        app = Wiverno(debug_mode=False)

        @app.get("/ok")
        def ok_handler(request):
            return 200, "OK"

        @app.post("/created")
        def created_handler(request):
            return 201, "Created"

        @app.put("/accepted")
        def accepted_handler(request):
            return 202, "Accepted"

        @app.delete("/deleted")
        def deleted_handler(request):
            return 204, ""

        test_cases = [
            ("/ok", "GET", "200 OK"),
            ("/created", "POST", "201 Created"),
            ("/accepted", "PUT", "202 Accepted"),
            ("/deleted", "DELETE", "204 No Content"),
        ]

        for path, method, expected_status in test_cases:
            status_line = None

            def start_response(status, headers):
                nonlocal status_line
                status_line = status

            app(make_environ(method=method, path=path), start_response)
            assert status_line == expected_status

    def test_various_error_codes(self):
        """Test various error status codes (4xx and 5xx)."""
        app = Wiverno(debug_mode=False)

        @app.get("/bad_request")
        def bad_request_handler(request):
            return 400, "Bad Request"

        @app.get("/not_found")
        def not_found_handler(request):
            return 404, "Not Found"

        @app.get("/server_error")
        def server_error_handler(request):
            return 500, "Server Error"

        test_cases = [
            ("/bad_request", "400 Bad Request"),
            ("/not_found", "404 Not Found"),
            ("/server_error", "500 Internal Server Error"),
        ]

        for path, expected_status in test_cases:
            status_line = None

            def start_response(status, headers):
                nonlocal status_line
                status_line = status

            app(make_environ(path=path), start_response)
            assert status_line == expected_status

    def test_string_and_int_status_produce_same_result(self):
        """Test that string and int status codes produce identical results."""
        app = Wiverno(debug_mode=False)

        @app.get("/int_status")
        def int_handler(request):
            return 201, "Created via int"

        @app.get("/string_status")
        def string_handler(request):
            return "201", "Created via string"

        def get_status(path):
            status_line = None

            def start_response(status, headers):
                nonlocal status_line
                status_line = status

            app(make_environ(path=path), start_response)
            return status_line

        int_status = get_status("/int_status")
        string_status = get_status("/string_status")

        assert int_status == string_status == "201 Created"

    def test_default_error_pages_unaffected(self):
        """Test that default error pages (404, 405) still work correctly."""
        app = Wiverno(debug_mode=False)

        @app.get("/existing")
        def handler(request):
            return "OK"

        # Test 404
        status_404 = None

        def start_response_404(status, headers):
            nonlocal status_404
            status_404 = status

        app(make_environ(path="/nonexistent"), start_response_404)
        assert status_404 == "404 Not Found"

        # Test 405
        status_405 = None

        def start_response_405(status, headers):
            nonlocal status_405
            status_405 = status

        app(make_environ(method="POST", path="/existing"), start_response_405)
        assert status_405 == "405 Method Not Allowed"

    def test_handler_with_dynamic_status_selection(self):
        """Test handler that dynamically selects status code based on query parameter."""
        app = Wiverno(debug_mode=False)

        @app.get("/status")
        def status_handler(request):
            # Get status code from query parameter
            code_str = request.query_params.get("code", "200")
            code = int(code_str)
            return code, f"Status {code}"

        test_cases = [
            (200, "200 OK"),
            (201, "201 Created"),
            (400, "400 Bad Request"),
            (404, "404 Not Found"),
            (500, "500 Internal Server Error"),
        ]

        for code, expected_status in test_cases:
            captured_status = None

            def capture_status(status, headers):
                nonlocal captured_status
                captured_status = status

            app(make_environ(path="/status", query=f"code={code}"), capture_status)
            assert captured_status == expected_status, f"Expected {expected_status} for code {code}, got {captured_status}"
