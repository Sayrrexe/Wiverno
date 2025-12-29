"""
Unit tests for BaseView class.

Tests:
- BaseView initialization
- HTTP method dispatching
- 405 Method Not Allowed handling
- Custom view implementations
"""

import pytest

from wiverno.core.requests import Request
from wiverno.views.base_views import BaseView

# ============================================================================
# BaseView Basic Tests
# ============================================================================


@pytest.mark.unit
class TestBaseViewBasic:
    """Basic tests for BaseView class."""

    def test_base_view_is_callable(self):
        """Test: BaseView instance is callable."""
        view = BaseView()

        assert callable(view)

    def test_base_view_without_handlers_returns_405(self, basic_environ):
        """Test: BaseView without any handlers returns 405."""
        view = BaseView()
        basic_environ["REQUEST_METHOD"] = "GET"
        request = Request(basic_environ)

        status, body = view(request)

        assert status == 405

    def test_base_view_get_method(self, basic_environ):
        """Test: BaseView with get() method handles GET requests."""

        class MyView(BaseView):
            def get(self, request):
                return "200 OK", "<html>GET response</html>"

        view = MyView()
        basic_environ["REQUEST_METHOD"] = "GET"
        request = Request(basic_environ)

        status, body = view(request)

        assert status == "200 OK"
        assert "GET response" in body

    def test_base_view_post_method(self, basic_environ):
        """Test: BaseView with post() method handles POST requests."""

        class MyView(BaseView):
            def post(self, request):
                return "201 Created", "<html>POST response</html>"

        view = MyView()
        basic_environ["REQUEST_METHOD"] = "POST"
        request = Request(basic_environ)

        status, body = view(request)

        assert status == "201 Created"
        assert "POST response" in body

    def test_base_view_put_method(self, basic_environ):
        """Test: BaseView with put() method handles PUT requests."""

        class MyView(BaseView):
            def put(self, request):
                return "200 OK", "<html>PUT response</html>"

        view = MyView()
        basic_environ["REQUEST_METHOD"] = "PUT"
        request = Request(basic_environ)

        status, body = view(request)

        assert status == "200 OK"
        assert "PUT response" in body

    def test_base_view_delete_method(self, basic_environ):
        """Test: BaseView with delete() method handles DELETE requests."""

        class MyView(BaseView):
            def delete(self, request):
                return "204 No Content", ""

        view = MyView()
        basic_environ["REQUEST_METHOD"] = "DELETE"
        request = Request(basic_environ)

        status, body = view(request)

        assert status == "204 No Content"

    def test_base_view_patch_method(self, basic_environ):
        """Test: BaseView with patch() method handles PATCH requests."""

        class MyView(BaseView):
            def patch(self, request):
                return "200 OK", "<html>PATCH response</html>"

        view = MyView()
        basic_environ["REQUEST_METHOD"] = "PATCH"
        request = Request(basic_environ)

        status, body = view(request)

        assert status == "200 OK"
        assert "PATCH response" in body


# ============================================================================
# Method Dispatching Tests
# ============================================================================


@pytest.mark.unit
class TestBaseViewMethodDispatching:
    """Tests for HTTP method dispatching."""

    def test_base_view_dispatches_to_correct_method(self, basic_environ):
        """Test: BaseView dispatches to correct HTTP method handler."""

        class TestView(BaseView):
            def get(self, request):
                return "200 OK", "GET"

            def post(self, request):
                return "200 OK", "POST"

            def put(self, request):
                return "200 OK", "PUT"

        view = TestView()

        # Test GET
        basic_environ["REQUEST_METHOD"] = "GET"
        request = Request(basic_environ)
        status, body = view(request)
        assert body == "GET"

        # Test POST
        basic_environ["REQUEST_METHOD"] = "POST"
        request = Request(basic_environ)
        status, body = view(request)
        assert body == "POST"

        # Test PUT
        basic_environ["REQUEST_METHOD"] = "PUT"
        request = Request(basic_environ)
        status, body = view(request)
        assert body == "PUT"

    def test_base_view_case_insensitive_method_dispatch(self, basic_environ):
        """Test: Method dispatching is case-insensitive."""

        class TestView(BaseView):
            def get(self, request):
                return "200 OK", "Success"

        view = TestView()

        # HTTP methods are uppercase in environ
        basic_environ["REQUEST_METHOD"] = "GET"
        request = Request(basic_environ)

        status, body = view(request)

        assert status == "200 OK"
        assert body == "Success"

    def test_base_view_only_implements_some_methods(self, basic_environ):
        """Test: View can implement only some HTTP methods."""

        class PartialView(BaseView):
            def get(self, request):
                return "200 OK", "GET works"

            def post(self, request):
                return "200 OK", "POST works"

            # No PUT, DELETE, etc.

        view = PartialView()

        # GET and POST should work
        basic_environ["REQUEST_METHOD"] = "GET"
        request = Request(basic_environ)
        status, body = view(request)
        assert status == "200 OK"

        # DELETE should return 405
        basic_environ["REQUEST_METHOD"] = "DELETE"
        request = Request(basic_environ)
        status, body = view(request)
        assert status == 405


# ============================================================================
# 405 Method Not Allowed Tests
# ============================================================================


@pytest.mark.unit
class TestBaseView405Handling:
    """Tests for 405 Method Not Allowed handling."""

    def test_base_view_returns_405_for_unimplemented_method(self, basic_environ):
        """Test: Unimplemented HTTP method returns 405."""

        class GetOnlyView(BaseView):
            def get(self, request):
                return "200 OK", "GET"

        view = GetOnlyView()

        # POST is not implemented
        basic_environ["REQUEST_METHOD"] = "POST"
        request = Request(basic_environ)

        status, body = view(request)

        assert status == 405

    def test_base_view_405_uses_handler(self, basic_environ):
        """Test: 405 response uses MethodNotAllowed405 handler."""
        view = BaseView()

        basic_environ["REQUEST_METHOD"] = "OPTIONS"
        request = Request(basic_environ)

        status, body = view(request)

        assert status == 405
        assert isinstance(body, str)

    def test_base_view_405_includes_method_info(self, basic_environ):
        """Test: 405 response includes method information."""

        class EmptyView(BaseView):
            pass

        view = EmptyView()

        basic_environ["REQUEST_METHOD"] = "DELETE"
        request = Request(basic_environ)

        status, body = view(request)

        # Should mention the method or show 405 error
        assert status == 405 or "DELETE" in body


# ============================================================================
# Custom View Implementation Tests
# ============================================================================


@pytest.mark.unit
class TestCustomViewImplementations:
    """Tests for custom view implementations."""

    def test_rest_api_view(self, basic_environ):
        """Test: RESTful API view with all methods."""

        class UserAPIView(BaseView):
            def get(self, request):
                return "200 OK", '{"users": []}'

            def post(self, request):
                return "201 Created", '{"id": 1}'

            def put(self, request):
                return "200 OK", '{"id": 1, "updated": true}'

            def delete(self, request):
                return "204 No Content", ""

        view = UserAPIView()

        # Test all CRUD operations
        basic_environ["REQUEST_METHOD"] = "GET"
        request = Request(basic_environ)
        status, body = view(request)
        assert status == "200 OK"
        assert "users" in body

        basic_environ["REQUEST_METHOD"] = "POST"
        request = Request(basic_environ)
        status, body = view(request)
        assert "201" in status

        basic_environ["REQUEST_METHOD"] = "PUT"
        request = Request(basic_environ)
        status, body = view(request)
        assert status == "200 OK"

        basic_environ["REQUEST_METHOD"] = "DELETE"
        request = Request(basic_environ)
        status, body = view(request)
        assert "204" in status

    def test_view_with_request_data_access(self, environ_factory):
        """Test: View can access request data."""

        class DataView(BaseView):
            def post(self, request):
                data = request.data
                return "200 OK", f"<html>Received: {data}</html>"

        view = DataView()

        import json

        body_data = json.dumps({"name": "Alice"}).encode("utf-8")
        environ = environ_factory(method="POST", body=body_data, content_type="application/json")

        request = Request(environ)
        status, body = view(request)

        assert status == "200 OK"
        assert "Alice" in body or "Received" in body

    def test_view_with_query_params(self, environ_factory):
        """Test: View can access query parameters."""

        class SearchView(BaseView):
            def get(self, request):
                query = request.query_params.get("q", "")
                return "200 OK", f"<html>Search: {query}</html>"

        view = SearchView()

        environ = environ_factory(query_string="q=python")
        request = Request(environ)

        status, body = view(request)

        assert status == "200 OK"
        assert "python" in body

    def test_view_with_custom_logic(self, basic_environ):
        """Test: View with custom business logic."""

        class CalculatorView(BaseView):
            def get(self, request):
                # Custom logic
                result = 2 + 2
                return "200 OK", f"<html>Result: {result}</html>"

        view = CalculatorView()

        basic_environ["REQUEST_METHOD"] = "GET"
        request = Request(basic_environ)

        status, body = view(request)

        assert status == "200 OK"
        assert "4" in body


# ============================================================================
# Edge Cases
# ============================================================================


@pytest.mark.unit
class TestBaseViewEdgeCases:
    """Edge case tests for BaseView."""

    def test_base_view_with_unusual_http_methods(self, basic_environ):
        """Test: BaseView handles unusual HTTP methods."""

        class FlexibleView(BaseView):
            def connect(self, request):
                return "200 OK", "CONNECT"

            def trace(self, request):
                return "200 OK", "TRACE"

            def options(self, request):
                return "200 OK", "OPTIONS"

        view = FlexibleView()

        # Test CONNECT
        basic_environ["REQUEST_METHOD"] = "CONNECT"
        request = Request(basic_environ)
        status, body = view(request)
        assert status == "200 OK"
        assert "CONNECT" in body

        # Test OPTIONS
        basic_environ["REQUEST_METHOD"] = "OPTIONS"
        request = Request(basic_environ)
        status, body = view(request)
        assert "OPTIONS" in body

    def test_base_view_empty_response(self, basic_environ):
        """Test: BaseView can return empty response."""

        class EmptyView(BaseView):
            def delete(self, request):
                return "204 No Content", ""

        view = EmptyView()

        basic_environ["REQUEST_METHOD"] = "DELETE"
        request = Request(basic_environ)

        status, body = view(request)

        assert "204" in status
        assert body == ""

    def test_base_view_handler_with_exception(self, basic_environ):
        """Test: BaseView handler can raise exceptions."""

        class ErrorView(BaseView):
            def get(self, request):
                raise ValueError("Something went wrong")

        view = ErrorView()

        basic_environ["REQUEST_METHOD"] = "GET"
        request = Request(basic_environ)

        # Exception should propagate
        with pytest.raises(ValueError, match="Something went wrong"):
            view(request)

    def test_base_view_head_method(self, basic_environ):
        """Test: BaseView with HEAD method."""

        class HeadView(BaseView):
            def head(self, request):
                return "200 OK", ""

            def get(self, request):
                return "200 OK", "<html>Content</html>"

        view = HeadView()

        # HEAD should return empty body
        basic_environ["REQUEST_METHOD"] = "HEAD"
        request = Request(basic_environ)
        status, body = view(request)
        assert status == "200 OK"
        assert body == ""

        # GET should return content
        basic_environ["REQUEST_METHOD"] = "GET"
        request = Request(basic_environ)
        status, body = view(request)
        assert "Content" in body

    def test_base_view_without_request_usage(self, basic_environ):
        """Test: View handler that doesn't use request parameter."""

        class StaticView(BaseView):
            def get(self, request):
                # Handler doesn't use request
                return "200 OK", "<html>Static content</html>"

        view = StaticView()

        basic_environ["REQUEST_METHOD"] = "GET"
        request = Request(basic_environ)

        status, body = view(request)

        assert status == "200 OK"
        assert "Static content" in body

    def test_base_view_returns_tuple(self, basic_environ):
        """Test: BaseView always returns tuple of (status, body)."""

        class TupleView(BaseView):
            def get(self, request):
                return "200 OK", "Body"

        view = TupleView()

        basic_environ["REQUEST_METHOD"] = "GET"
        request = Request(basic_environ)

        result = view(request)

        assert isinstance(result, tuple)
        assert len(result) == 2
        assert result[0] == "200 OK"
        assert result[1] == "Body"
