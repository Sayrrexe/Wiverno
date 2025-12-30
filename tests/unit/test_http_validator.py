"""
Unit tests for HTTP status validation utilities.

Tests cover HTTPStatusValidator class and InvalidHTTPStatusError exception
to ensure proper validation and normalization of HTTP status codes.
"""

import pytest

from wiverno.core.exceptions import InvalidHTTPStatusError
from wiverno.core.http.validator import HTTPStatusValidator


class TestHTTPStatusValidator:
    """Test suite for HTTPStatusValidator.normalize_status method."""

    def test_normalize_status_from_int(self):
        """Test normalization from integer status code."""
        result = HTTPStatusValidator.normalize_status(200)
        assert result == "200 OK"

    def test_normalize_status_from_int_404(self):
        """Test normalization from integer 404."""
        result = HTTPStatusValidator.normalize_status(404)
        assert result == "404 Not Found"

    def test_normalize_status_from_int_500(self):
        """Test normalization from integer 500."""
        result = HTTPStatusValidator.normalize_status(500)
        assert result == "500 Internal Server Error"

    def test_normalize_status_from_string_code_only(self):
        """Test normalization from string containing only status code."""
        result = HTTPStatusValidator.normalize_status("201")
        assert result == "201 Created"

    def test_normalize_status_from_string_with_phrase(self):
        """Test normalization from string with code and phrase."""
        result = HTTPStatusValidator.normalize_status("200 OK")
        assert result == "200 OK"

    def test_normalize_status_from_string_with_wrong_phrase(self):
        """Test that validator fixes incorrect reason phrases."""
        result = HTTPStatusValidator.normalize_status("404 Wrong Phrase")
        assert result == "404 Not Found"

    def test_normalize_status_from_string_with_extra_spaces(self):
        """Test normalization handles extra whitespace."""
        result = HTTPStatusValidator.normalize_status("  200   OK  ")
        assert result == "200 OK"

    def test_normalize_status_common_codes(self):
        """Test normalization for common HTTP status codes."""
        test_cases = [
            (200, "200 OK"),
            (201, "201 Created"),
            (204, "204 No Content"),
            (301, "301 Moved Permanently"),
            (302, "302 Found"),
            (400, "400 Bad Request"),
            (401, "401 Unauthorized"),
            (403, "403 Forbidden"),
            (404, "404 Not Found"),
            (405, "405 Method Not Allowed"),
            (500, "500 Internal Server Error"),
            (502, "502 Bad Gateway"),
            (503, "503 Service Unavailable"),
        ]
        for code, expected in test_cases:
            assert HTTPStatusValidator.normalize_status(code) == expected

    def test_normalize_status_from_string_code(self):
        """Test normalization from string representation of codes."""
        test_cases = [
            ("200", "200 OK"),
            ("404", "404 Not Found"),
            ("500", "500 Internal Server Error"),
        ]
        for code, expected in test_cases:
            assert HTTPStatusValidator.normalize_status(code) == expected

    def test_normalize_status_invalid_type_none(self):
        """Test that None raises InvalidHTTPStatusError."""
        with pytest.raises(InvalidHTTPStatusError) as exc_info:
            HTTPStatusValidator.normalize_status(None)
        assert exc_info.value.status == "unknown"

    def test_normalize_status_invalid_type_float(self):
        """Test that float raises InvalidHTTPStatusError."""
        with pytest.raises(InvalidHTTPStatusError):
            HTTPStatusValidator.normalize_status(200.5)

    def test_normalize_status_invalid_type_list(self):
        """Test that list raises InvalidHTTPStatusError."""
        with pytest.raises(InvalidHTTPStatusError):
            HTTPStatusValidator.normalize_status([200])

    def test_normalize_status_invalid_type_dict(self):
        """Test that dict raises InvalidHTTPStatusError."""
        with pytest.raises(InvalidHTTPStatusError):
            HTTPStatusValidator.normalize_status({"code": 200})

    def test_normalize_status_invalid_string_non_numeric(self):
        """Test that non-numeric string raises InvalidHTTPStatusError."""
        with pytest.raises(InvalidHTTPStatusError) as exc_info:
            HTTPStatusValidator.normalize_status("OK")
        assert exc_info.value.status == "OK"

    def test_normalize_status_invalid_string_empty(self):
        """Test that empty string raises InvalidHTTPStatusError."""
        with pytest.raises(InvalidHTTPStatusError) as exc_info:
            HTTPStatusValidator.normalize_status("")
        assert exc_info.value.status == ""

    def test_normalize_status_unknown_code(self):
        """Test that unknown HTTP code raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            HTTPStatusValidator.normalize_status(999)
        assert "Unknown HTTP status code: 999" in str(exc_info.value)

    def test_normalize_status_unknown_code_as_string(self):
        """Test that unknown HTTP code as string raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            HTTPStatusValidator.normalize_status("999")
        assert "Unknown HTTP status code: 999" in str(exc_info.value)

    def test_normalize_status_negative_code(self):
        """Test that negative status code raises ValueError."""
        with pytest.raises(ValueError):
            HTTPStatusValidator.normalize_status(-1)

    def test_normalize_status_zero_code(self):
        """Test that zero status code raises ValueError."""
        with pytest.raises(ValueError):
            HTTPStatusValidator.normalize_status(0)

    def test_normalize_status_string_with_negative_code(self):
        """Test that negative code as string raises InvalidHTTPStatusError."""
        with pytest.raises(InvalidHTTPStatusError):
            HTTPStatusValidator.normalize_status("-200")

    def test_normalize_status_informational_codes(self):
        """Test normalization for 1xx informational status codes."""
        test_cases = [
            (100, "100 Continue"),
            (101, "101 Switching Protocols"),
            (102, "102 Processing"),
        ]
        for code, expected in test_cases:
            assert HTTPStatusValidator.normalize_status(code) == expected

    def test_normalize_status_redirection_codes(self):
        """Test normalization for 3xx redirection status codes."""
        test_cases = [
            (300, "300 Multiple Choices"),
            (301, "301 Moved Permanently"),
            (302, "302 Found"),
            (303, "303 See Other"),
            (304, "304 Not Modified"),
            (307, "307 Temporary Redirect"),
            (308, "308 Permanent Redirect"),
        ]
        for code, expected in test_cases:
            assert HTTPStatusValidator.normalize_status(code) == expected

    def test_normalize_status_client_error_codes(self):
        """Test normalization for 4xx client error status codes."""
        test_cases = [
            (400, "400 Bad Request"),
            (401, "401 Unauthorized"),
            (402, "402 Payment Required"),
            (403, "403 Forbidden"),
            (404, "404 Not Found"),
            (405, "405 Method Not Allowed"),
            (406, "406 Not Acceptable"),
            (408, "408 Request Timeout"),
            (409, "409 Conflict"),
            (410, "410 Gone"),
            (414, "414 Request-URI Too Long"),
            (415, "415 Unsupported Media Type"),
            (418, "418 I'm a Teapot"),
            (422, "422 Unprocessable Entity"),
            (429, "429 Too Many Requests"),
        ]
        for code, expected in test_cases:
            assert HTTPStatusValidator.normalize_status(code) == expected

    def test_normalize_status_server_error_codes(self):
        """Test normalization for 5xx server error status codes."""
        test_cases = [
            (500, "500 Internal Server Error"),
            (501, "501 Not Implemented"),
            (502, "502 Bad Gateway"),
            (503, "503 Service Unavailable"),
            (504, "504 Gateway Timeout"),
            (505, "505 HTTP Version Not Supported"),
        ]
        for code, expected in test_cases:
            assert HTTPStatusValidator.normalize_status(code) == expected


class TestInvalidHTTPStatusError:
    """Test suite for InvalidHTTPStatusError exception."""

    def test_exception_with_status(self):
        """Test exception initialization with status value."""
        error = InvalidHTTPStatusError("invalid_status")
        assert error.status == "invalid_status"
        assert "Invalid HTTP status: 'invalid_status'" in str(error)

    def test_exception_without_status(self):
        """Test exception initialization without status value."""
        error = InvalidHTTPStatusError()
        assert error.status == "unknown"
        assert "Invalid HTTP status: 'unknown'" in str(error)

    def test_exception_with_none_status(self):
        """Test exception initialization with None."""
        error = InvalidHTTPStatusError(None)
        assert error.status == "unknown"
        assert "Invalid HTTP status: 'unknown'" in str(error)

    def test_exception_with_empty_string(self):
        """Test exception initialization with empty string."""
        error = InvalidHTTPStatusError("")
        assert error.status == ""
        assert "Invalid HTTP status: ''" in str(error)

    def test_exception_is_exception_subclass(self):
        """Test that InvalidHTTPStatusError is a proper Exception."""
        error = InvalidHTTPStatusError("test")
        assert isinstance(error, Exception)

    def test_exception_can_be_raised(self):
        """Test that exception can be raised and caught."""
        with pytest.raises(InvalidHTTPStatusError) as exc_info:
            raise InvalidHTTPStatusError("test_status")
        assert exc_info.value.status == "test_status"

    def test_exception_message_format(self):
        """Test exception message formatting with various status values."""
        test_cases = [
            ("200", "Invalid HTTP status: '200'"),
            (123, "Invalid HTTP status: 123"),
            ({"code": 200}, "Invalid HTTP status: {'code': 200}"),
            ([200], "Invalid HTTP status: [200]"),
        ]
        for status, expected_msg in test_cases:
            error = InvalidHTTPStatusError(status)
            assert expected_msg in str(error)


class TestHTTPValidatorIntegration:
    """Integration tests for HTTP validator in realistic scenarios."""

    def test_validator_with_wsgi_response(self):
        """Test validator works with typical WSGI response status."""
        # Simulating what a view handler might return
        handler_returns = [
            (200, "200 OK"),
            ("201", "201 Created"),
            ("404 Not Found", "404 Not Found"),
            (500, "500 Internal Server Error"),
        ]
        for input_status, expected in handler_returns:
            result = HTTPStatusValidator.normalize_status(input_status)
            assert result == expected

    def test_validator_handles_malformed_inputs(self):
        """Test validator properly handles malformed status inputs."""
        malformed_inputs = [
            None,
            [],
            {},
            "",
            "not a code",
            "OK 200",  # Reversed order
        ]
        for bad_input in malformed_inputs:
            with pytest.raises(InvalidHTTPStatusError):
                HTTPStatusValidator.normalize_status(bad_input)

    def test_validator_consistency_string_vs_int(self):
        """Test that string and int inputs produce identical results."""
        codes = [200, 201, 204, 301, 400, 404, 500, 502]
        for code in codes:
            int_result = HTTPStatusValidator.normalize_status(code)
            str_result = HTTPStatusValidator.normalize_status(str(code))
            assert int_result == str_result

    def test_error_attribute_preserved(self):
        """Test that InvalidHTTPStatusError preserves the original value."""
        bad_values = ["invalid", None, 999, {"code": 200}]
        for value in bad_values:
            try:
                HTTPStatusValidator.normalize_status(value)
            except (InvalidHTTPStatusError, ValueError) as e:
                if isinstance(e, InvalidHTTPStatusError):
                    # Error should preserve the original bad value
                    assert hasattr(e, "status")
                    # For None, it should be "unknown"
                    if value is None:
                        assert e.status == "unknown"
