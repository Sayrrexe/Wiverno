"""
Unit tests for PathPattern class and compile_path function.

Tests:
- Path compilation with different parameter types
- Parameter extraction and type conversion
- Pattern matching
- Prefix handling
- Edge cases and error handling
"""

import pytest

from wiverno.core.routing.patterns import PathPattern, compile_path


# ============================================================================
# Path Compilation Tests
# ============================================================================


@pytest.mark.unit
class TestPathCompilation:
    """Tests for compile_path function."""

    def test_compile_simple_path(self):
        """Test: Compile simple path with one parameter."""
        pattern = compile_path("/users/{id}")

        assert pattern.pattern_str == "/users/{id}"
        assert pattern.param_names == ("id",)
        assert pattern.converters == {"id": str}

    def test_compile_typed_int_path(self):
        """Test: Compile path with int type parameter."""
        pattern = compile_path("/users/{id:int}")

        assert pattern.pattern_str == "/users/{id:int}"
        assert pattern.param_names == ("id",)
        assert pattern.converters == {"id": int}

    def test_compile_typed_float_path(self):
        """Test: Compile path with float type parameter."""
        pattern = compile_path("/items/{price:float}")

        assert pattern.pattern_str == "/items/{price:float}"
        assert pattern.param_names == ("price",)
        assert pattern.converters == {"price": float}

    def test_compile_typed_str_path(self):
        """Test: Compile path with explicit str type parameter."""
        pattern = compile_path("/users/{name:str}")

        assert pattern.pattern_str == "/users/{name:str}"
        assert pattern.param_names == ("name",)
        assert pattern.converters == {"name": str}

    def test_compile_path_type_parameter(self):
        """Test: Compile path with path type parameter (matches slashes)."""
        pattern = compile_path("/files/{filepath:path}")

        assert pattern.pattern_str == "/files/{filepath:path}"
        assert pattern.param_names == ("filepath",)
        assert pattern.converters == {"filepath": str}

    def test_compile_multiple_params(self):
        """Test: Compile path with multiple parameters."""
        pattern = compile_path("/users/{user_id}/posts/{post_id}")

        assert pattern.pattern_str == "/users/{user_id}/posts/{post_id}"
        assert pattern.param_names == ("user_id", "post_id")
        assert "user_id" in pattern.converters
        assert "post_id" in pattern.converters

    def test_compile_mixed_types(self):
        """Test: Compile path with mixed parameter types."""
        pattern = compile_path("/users/{user_id:int}/posts/{slug:str}")

        assert pattern.param_names == ("user_id", "slug")
        assert pattern.converters == {"user_id": int, "slug": str}

    def test_segments_count(self):
        """Test: Segments count is calculated correctly."""
        pattern1 = compile_path("/users/{id}")
        pattern2 = compile_path("/users/{id}/posts/{post_id}")
        pattern3 = compile_path("/")

        assert pattern1.segments_count == 2  # / and /users
        assert pattern2.segments_count == 4  # /, /users, /, /posts
        assert pattern3.segments_count == 1  # /

    def test_compile_static_path(self):
        """Test: Compile static path (no parameters)."""
        pattern = compile_path("/users/list")

        assert pattern.pattern_str == "/users/list"
        assert pattern.param_names == ()
        assert pattern.converters == {}

    def test_too_many_parameters_protection(self):
        """Test: ReDoS protection - limit number of parameters."""
        path = "/" + "/".join([f"{{param{i}}}" for i in range(21)])

        with pytest.raises(ValueError, match="Too many parameters"):
            compile_path(path)


# ============================================================================
# Pattern Matching Tests
# ============================================================================


@pytest.mark.unit
class TestPatternMatching:
    """Tests for PathPattern.match method."""

    def test_match_simple_pattern(self):
        """Test: Match simple path with parameter."""
        pattern = compile_path("/users/{id}")

        result = pattern.match("/users/123")

        assert result is not None
        assert result == {"id": "123"}

    def test_match_int_conversion(self):
        """Test: Match and convert int parameter."""
        pattern = compile_path("/users/{id:int}")

        result = pattern.match("/users/42")

        assert result is not None
        assert result == {"id": 42}
        assert isinstance(result["id"], int)

    def test_match_float_conversion(self):
        """Test: Match and convert float parameter."""
        pattern = compile_path("/items/{price:float}")

        result = pattern.match("/items/19.99")

        assert result is not None
        assert result["price"] == 19.99
        assert isinstance(result["price"], float)

    def test_match_float_integer_value(self):
        """Test: Match float parameter with integer value."""
        pattern = compile_path("/items/{price:float}")

        result = pattern.match("/items/20")

        assert result is not None
        assert result["price"] == 20.0

    def test_match_multiple_params(self):
        """Test: Match and extract multiple parameters."""
        pattern = compile_path("/users/{user_id:int}/posts/{post_id:int}")

        result = pattern.match("/users/5/posts/42")

        assert result is not None
        assert result == {"user_id": 5, "post_id": 42}

    def test_match_str_parameter(self):
        """Test: Match string parameter."""
        pattern = compile_path("/users/{username:str}")

        result = pattern.match("/users/alice")

        assert result is not None
        assert result == {"username": "alice"}

    def test_match_path_parameter(self):
        """Test: Match path parameter (includes slashes)."""
        pattern = compile_path("/files/{filepath:path}")

        result = pattern.match("/files/documents/report.pdf")

        assert result is not None
        assert result == {"filepath": "documents/report.pdf"}

    def test_no_match_wrong_path(self):
        """Test: Return None for non-matching path."""
        pattern = compile_path("/users/{id}")

        result = pattern.match("/posts/123")

        assert result is None

    def test_no_match_extra_segments(self):
        """Test: Return None for path with extra segments."""
        pattern = compile_path("/users/{id}")

        result = pattern.match("/users/123/extra")

        assert result is None

    def test_invalid_int_conversion(self):
        """Test: Invalid int conversion returns string."""
        pattern = compile_path("/users/{id:int}")

        result = pattern.match("/users/abc")

        # Since regex doesn't match, result should be None
        assert result is None

    def test_match_with_special_chars(self):
        """Test: Match parameter with special characters."""
        pattern = compile_path("/tags/{name}")

        result = pattern.match("/tags/python-3.11")

        assert result is not None
        assert result == {"name": "python-3.11"}


# ============================================================================
# Prefix Tests
# ============================================================================


@pytest.mark.unit
class TestPatternPrefix:
    """Tests for PathPattern.with_prefix method."""

    def test_with_prefix_simple(self):
        """Test: Add simple prefix to pattern."""
        pattern = compile_path("/users/{id}")

        new_pattern = pattern.with_prefix("/api")

        assert new_pattern.pattern_str == "/api/users/{id}"
        assert new_pattern.param_names == ("id",)

    def test_with_prefix_empty(self):
        """Test: Empty prefix creates new pattern."""
        pattern = compile_path("/users/{id}")

        new_pattern = pattern.with_prefix("")

        assert new_pattern.pattern_str == "/users/{id}"

    def test_with_prefix_nested(self):
        """Test: Add nested prefix."""
        pattern = compile_path("/users/{id}")

        new_pattern = pattern.with_prefix("/api/v1")

        assert new_pattern.pattern_str == "/api/v1/users/{id}"

    def test_with_prefix_preserves_types(self):
        """Test: Prefix preserves parameter types."""
        pattern = compile_path("/users/{id:int}")

        new_pattern = pattern.with_prefix("/api")

        assert new_pattern.converters == {"id": int}
        assert new_pattern.param_names == ("id",)

    def test_with_prefix_matching(self):
        """Test: Prefixed pattern matches correctly."""
        pattern = compile_path("/users/{id:int}")
        prefixed = pattern.with_prefix("/api")

        result = prefixed.match("/api/users/42")

        assert result is not None
        assert result == {"id": 42}


# ============================================================================
# Edge Cases
# ============================================================================


@pytest.mark.unit
class TestPatternEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_compile_root_path(self):
        """Test: Compile root path."""
        pattern = compile_path("/")

        assert pattern.pattern_str == "/"
        assert pattern.param_names == ()
        assert pattern.segments_count == 1

    def test_match_root_path(self):
        """Test: Match root path."""
        pattern = compile_path("/")

        result = pattern.match("/")

        assert result is not None
        assert result == {}

    def test_pattern_immutability(self):
        """Test: PathPattern is immutable (frozen dataclass)."""
        from dataclasses import FrozenInstanceError

        pattern = compile_path("/users/{id}")

        with pytest.raises(FrozenInstanceError):
            pattern.pattern_str = "/changed"  # type: ignore

    def test_zero_float_conversion(self):
        """Test: Zero float conversion."""
        pattern = compile_path("/items/{price:float}")

        result = pattern.match("/items/0")

        assert result is not None
        assert result["price"] == 0.0

    def test_negative_int_not_matched(self):
        """Test: Negative integers don't match int pattern."""
        pattern = compile_path("/items/{id:int}")

        result = pattern.match("/items/-5")

        # Regex [0-9]+ doesn't match negative
        assert result is None
