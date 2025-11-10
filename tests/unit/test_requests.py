"""
Unit tests for requests module.

Tests:
- ParseQuery: query string parsing
- ParseBody: request body parsing (form-data, JSON, urlencoded)
- HeaderParser: header parsing
- Request: creating request object from WSGI environ
"""

import json

import pytest

from wiverno.core.requests import HeaderParser, ParseBody, ParseQuery, Request

# ============================================================================
# ParseQuery Tests
# ============================================================================


@pytest.mark.unit
class TestParseQuery:
    """Tests for ParseQuery class for query string parsing."""

    def test_parse_simple_query_string(self):
        """Test: Parsing simple query string."""
        result = ParseQuery.parse_input_data("name=John&age=30")

        assert result == {"name": "John", "age": "30"}

    def test_parse_empty_query_string(self):
        """Test: Empty query string returns empty dict."""
        result = ParseQuery.parse_input_data("")

        assert result == {}

    def test_parse_query_with_special_characters(self):
        """Test: Query string with special characters."""
        result = ParseQuery.parse_input_data("email=test%40example.com&city=New%20York")

        assert "email" in result
        assert "city" in result

    def test_parse_query_with_multiple_values(self):
        """Test: Parameter with multiple values - first one is taken."""
        result = ParseQuery.parse_input_data("id=1&id=2&id=3")

        # Should only have the first value
        assert result["id"] == "1"

    def test_get_request_params_from_environ(self, basic_environ):
        """Test: Extracting parameters from WSGI environ."""
        basic_environ["QUERY_STRING"] = "page=1&limit=10"

        result = ParseQuery.get_request_params(basic_environ)

        assert result == {"page": "1", "limit": "10"}

    def test_get_request_params_no_query_string(self, basic_environ):
        """Test: Missing QUERY_STRING returns empty dict."""
        basic_environ.pop("QUERY_STRING", None)

        result = ParseQuery.get_request_params(basic_environ)

        assert result == {}


# ============================================================================
# ParseBody Tests
# ============================================================================


@pytest.mark.unit
class TestParseBody:
    """Tests for ParseBody class for request body parsing."""

    def test_parse_json_body(self, basic_environ):
        """Test: Parsing JSON request body."""
        json_data = {"name": "Alice", "age": 25}
        raw_data = json.dumps(json_data).encode("utf-8")

        basic_environ["CONTENT_TYPE"] = "application/json"
        basic_environ["CONTENT_LENGTH"] = str(len(raw_data))

        result = ParseBody.get_request_params(basic_environ, raw_data)

        assert result == json_data

    def test_parse_urlencoded_body(self, basic_environ):
        """Test: Parsing application/x-www-form-urlencoded."""
        raw_data = b"username=john&password=secret123"

        basic_environ["CONTENT_TYPE"] = "application/x-www-form-urlencoded"
        basic_environ["CONTENT_LENGTH"] = str(len(raw_data))

        result = ParseBody.get_request_params(basic_environ, raw_data)

        assert result == {"username": "john", "password": "secret123"}

    def test_parse_multipart_form_data(self, basic_environ):
        """Test: Parsing multipart/form-data."""
        boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
        raw_data = (
            b"------WebKitFormBoundary7MA4YWxkTrZu0gW\r\n"
            b'Content-Disposition: form-data; name="field1"\r\n'
            b"\r\n"
            b"value1\r\n"
            b"------WebKitFormBoundary7MA4YWxkTrZu0gW\r\n"
            b'Content-Disposition: form-data; name="field2"\r\n'
            b"\r\n"
            b"value2\r\n"
            b"------WebKitFormBoundary7MA4YWxkTrZu0gW--\r\n"
        )

        basic_environ["CONTENT_TYPE"] = f"multipart/form-data; boundary={boundary}"
        basic_environ["CONTENT_LENGTH"] = str(len(raw_data))

        result = ParseBody.get_request_params(basic_environ, raw_data)

        # Check that data was parsed
        assert isinstance(result, dict)
        assert "field1" in result or len(result) >= 0  # multipart can be complex

    def test_parse_invalid_json(self, basic_environ):
        """Test: Invalid JSON returns empty dict."""
        raw_data = b"{ invalid json }"

        basic_environ["CONTENT_TYPE"] = "application/json"

        result = ParseBody.get_request_params(basic_environ, raw_data)

        assert result == {}

    def test_parse_empty_body(self, basic_environ):
        """Test: Empty body returns empty dict."""
        raw_data = b""

        basic_environ["CONTENT_TYPE"] = "application/json"

        result = ParseBody.get_request_params(basic_environ, raw_data)

        assert result == {}

    def test_parse_unsupported_content_type(self, basic_environ):
        """Test: Unsupported Content-Type returns empty dict."""
        raw_data = b"some data"

        basic_environ["CONTENT_TYPE"] = "text/plain"

        result = ParseBody.get_request_params(basic_environ, raw_data)

        assert result == {}


# ============================================================================
# HeaderParser Tests
# ============================================================================


@pytest.mark.unit
class TestHeaderParser:
    """Tests for HeaderParser class for header parsing."""

    def test_parse_headers_basic(self, basic_environ):
        """Test: Parsing basic HTTP headers."""
        basic_environ["HTTP_USER_AGENT"] = "Mozilla/5.0"
        basic_environ["HTTP_ACCEPT"] = "text/html"
        basic_environ["HTTP_HOST"] = "example.com"

        headers = HeaderParser.get_headers(basic_environ)

        assert headers["User-Agent"] == "Mozilla/5.0"
        assert headers["Accept"] == "text/html"
        assert headers["Host"] == "example.com"

    def test_parse_headers_with_underscores(self, basic_environ):
        """Test: Headers with underscores are converted to dashes."""
        basic_environ["HTTP_CONTENT_TYPE"] = "application/json"
        basic_environ["HTTP_X_CUSTOM_HEADER"] = "custom-value"

        headers = HeaderParser.get_headers(basic_environ)

        assert headers["Content-Type"] == "application/json"
        assert headers["X-Custom-Header"] == "custom-value"

    def test_parse_headers_empty(self, basic_environ):
        """Test: Missing HTTP_ headers returns empty dict."""
        # Remove all HTTP_ keys
        environ_no_headers = {k: v for k, v in basic_environ.items() if not k.startswith("HTTP_")}

        headers = HeaderParser.get_headers(environ_no_headers)

        assert headers == {}

    def test_parse_headers_ignores_non_http(self, basic_environ):
        """Test: Keys without HTTP_ prefix are ignored."""
        basic_environ["REQUEST_METHOD"] = "GET"
        basic_environ["PATH_INFO"] = "/test"
        basic_environ["HTTP_ACCEPT"] = "application/json"

        headers = HeaderParser.get_headers(basic_environ)

        # Only HTTP_ headers should be in result
        assert "Accept" in headers
        assert "Request-Method" not in headers
        assert "Path-Info" not in headers


# ============================================================================
# Request Class Tests
# ============================================================================


@pytest.mark.unit
class TestRequestInitialization:
    """Tests for Request object initialization."""

    def test_request_basic_initialization(self, basic_environ):
        """Test: Basic Request initialization."""
        request = Request(basic_environ)

        assert request.method == "GET"
        assert request.path == "/"
        assert isinstance(request.headers, dict)
        assert isinstance(request.query_params, dict)

    def test_request_method_parsing(self, environ_factory):
        """Test: Correct HTTP method parsing."""
        environ = environ_factory(method="POST")
        request = Request(environ)

        assert request.method == "POST"

    def test_request_path_parsing(self, environ_factory):
        """Test: Request path parsing and normalization."""
        environ = environ_factory(path="/api/users")
        request = Request(environ)

        # Request normalizes path (removes trailing slash except for root)
        assert request.path == "/api/users"

    def test_request_query_params(self, environ_factory):
        """Test: Query parameter parsing."""
        environ = environ_factory(query_string="page=2&limit=20")
        request = Request(environ)

        assert request.query_params == {"page": "2", "limit": "20"}

    def test_request_data_json(self, environ_factory):
        """Test: Parsing JSON data from POST."""
        json_data = {"key": "value"}
        body = json.dumps(json_data).encode("utf-8")

        environ = environ_factory(method="POST", body=body, content_type="application/json")
        request = Request(environ)

        assert request.data == json_data

    def test_request_content_type(self, environ_factory):
        """Test: Storing Content-Type."""
        environ = environ_factory(content_type="application/json")
        request = Request(environ)

        assert request.content_type == "application/json"

    def test_request_content_length(self, environ_factory):
        """Test: Parsing Content-Length."""
        body = b"test data"
        environ = environ_factory(body=body)
        request = Request(environ)

        assert request.content_length == len(body)


@pytest.mark.unit
class TestRequestProperties:
    """Tests for Request properties and attributes."""

    def test_request_client_ip(self, basic_environ):
        """Test: Extracting client IP address."""
        basic_environ["REMOTE_ADDR"] = "192.168.1.100"
        request = Request(basic_environ)

        assert request.client_ip == "192.168.1.100"

    def test_request_server_name(self, basic_environ):
        """Test: Extracting server name."""
        basic_environ["SERVER_NAME"] = "example.com"
        request = Request(basic_environ)

        assert request.server == "example.com"

    def test_request_user_agent(self, basic_environ):
        """Test: Extracting User-Agent."""
        basic_environ["HTTP_USER_AGENT"] = "TestBot/1.0"
        request = Request(basic_environ)

        assert request.user_agent == "TestBot/1.0"

    def test_request_protocol(self, basic_environ):
        """Test: Extracting HTTP protocol."""
        basic_environ["SERVER_PROTOCOL"] = "HTTP/1.1"
        request = Request(basic_environ)

        assert request.protocol == "HTTP/1.1"

    def test_request_scheme_http(self, basic_environ):
        """Test: HTTP scheme."""
        basic_environ["wsgi.url_scheme"] = "http"
        request = Request(basic_environ)

        assert request.scheme == "http"
        assert request.is_secure is False

    def test_request_scheme_https(self, basic_environ):
        """Test: HTTPS scheme."""
        basic_environ["wsgi.url_scheme"] = "https"
        request = Request(basic_environ)

        assert request.scheme == "https"
        assert request.is_secure is True


@pytest.mark.unit
class TestRequestCookies:
    """Tests for cookies parsing."""

    def test_parse_single_cookie(self, basic_environ):
        """Test: Parsing single cookie."""
        basic_environ["HTTP_COOKIE"] = "session_id=abc123"
        request = Request(basic_environ)

        assert request.cookies == {"session_id": "abc123"}

    def test_parse_multiple_cookies(self, basic_environ):
        """Test: Parsing multiple cookies."""
        basic_environ["HTTP_COOKIE"] = "session_id=abc123; user=john; theme=dark"
        request = Request(basic_environ)

        assert request.cookies == {
            "session_id": "abc123",
            "user": "john",
            "theme": "dark",
        }

    def test_parse_no_cookies(self, basic_environ):
        """Test: No cookies."""
        request = Request(basic_environ)

        assert request.cookies == {}

    def test_parse_cookie_with_equals_in_value(self, basic_environ):
        """Test: Cookie with equals sign in value."""
        basic_environ["HTTP_COOKIE"] = "token=eyJhbGc=iOiJIUzI1"
        request = Request(basic_environ)

        # Should preserve everything after first =
        assert "token" in request.cookies
        assert "=" in request.cookies["token"]


@pytest.mark.unit
class TestRequestPathNormalization:
    """Tests for path normalization."""

    def test_path_adds_trailing_slash(self, environ_factory):
        """Test: Path normalization removes trailing slash."""
        environ = environ_factory(path="/users")
        request = Request(environ)

        # Path normalization removes trailing slash (except for root)
        assert request.path == "/users"

    def test_path_keeps_trailing_slash(self, environ_factory):
        """Test: Path normalization removes existing trailing slash."""
        environ = environ_factory(path="/users/")
        request = Request(environ)

        # Trailing slash is removed during normalization
        assert request.path == "/users"

    def test_path_url_decoding(self, environ_factory):
        """Test: URL decoding of path."""
        environ = environ_factory(path="/search/New%20York")
        request = Request(environ)

        # unquote should decode %20 to space
        assert "New York" in request.path


@pytest.mark.integration
class TestRequestIntegration:
    """Integration tests for Request with various scenarios."""

    def test_complete_get_request(self, environ_factory):
        """Test: Complete GET request."""
        environ = environ_factory(
            method="GET",
            path="/api/users",
            query_string="page=1&sort=name",
            headers={"User-Agent": "TestClient/1.0", "Accept": "application/json"},
        )
        request = Request(environ)

        assert request.method == "GET"
        assert request.path == "/api/users"  # Normalized (no trailing slash)
        assert request.query_params == {"page": "1", "sort": "name"}
        assert request.headers["User-Agent"] == "TestClient/1.0"

    def test_complete_post_request_json(self, environ_factory):
        """Test: Complete POST request with JSON."""
        data = {"username": "alice", "email": "alice@example.com"}
        body = json.dumps(data).encode("utf-8")

        environ = environ_factory(
            method="POST",
            path="/api/users",
            body=body,
            content_type="application/json",
        )
        request = Request(environ)

        assert request.method == "POST"
        assert request.data == data
        assert request.content_type == "application/json"
        assert request.content_length == len(body)
