"""
Performance tests (benchmarks) for Wiverno.

Uses pytest-benchmark to measure performance
of critical framework components.

Run:
    pytest tests/benchmark/test_benchmark.py --benchmark-only
    pytest tests/benchmark/test_benchmark.py --benchmark-compare
    pytest tests/benchmark/test_benchmark.py --benchmark-autosave
"""

import json

import pytest

from wiverno.core.requests import HeaderParser, ParseBody, ParseQuery, Request
from wiverno.core.router import Router
from wiverno.main import Wiverno
from wiverno.templating.templator import Templator

# ============================================================================
# Router Benchmarks
# ============================================================================


@pytest.mark.benchmark
class TestRouterBenchmarks:
    """Router performance benchmarks."""

    def test_benchmark_route_registration(self, benchmark):
        """Benchmark: Route registration via decorator."""

        def register_route():
            router = Router()

            @router.get("/test")
            def handler(request):
                return "200 OK", "Test"

            return router

        result = benchmark(register_route)
        assert len(result._routes) == 1

    def test_benchmark_multiple_route_registration(self, benchmark):
        """Benchmark: Registering multiple routes."""

        def register_multiple_routes():
            router = Router()
            for i in range(100):
                router.add_route(f"/route{i}", lambda req: ("200 OK", "OK"))
            return router

        result = benchmark(register_multiple_routes)
        assert len(result._routes) == 100

    def test_benchmark_route_lookup(self, benchmark, router_with_routes):
        """Benchmark: Route lookup in list."""

        def lookup_route():
            # Simulate route lookup
            for route in router_with_routes._routes:
                if route["path"] == "/users":
                    return route
            return None

        result = benchmark(lookup_route)
        assert result is not None


# ============================================================================
# Request Benchmarks
# ============================================================================


@pytest.mark.benchmark
class TestRequestBenchmarks:
    """Request processing performance benchmarks."""

    def test_benchmark_request_creation(self, benchmark, basic_environ):
        """Benchmark: Creating Request object."""
        result = benchmark(Request, basic_environ)
        assert result.method == "GET"

    def test_benchmark_parse_query_string(self, benchmark):
        """Benchmark: Parsing query string."""
        query = "page=1&limit=20&sort=name&order=asc&filter=active"

        result = benchmark(ParseQuery.parse_input_data, query)
        assert len(result) == 5

    def test_benchmark_parse_json_body(self, benchmark, basic_environ):
        """Benchmark: Parsing JSON request body."""
        data = {"user": "alice", "age": 30, "email": "alice@example.com"}
        raw_data = json.dumps(data).encode("utf-8")

        basic_environ["CONTENT_TYPE"] = "application/json"

        result = benchmark(ParseBody.get_request_params, basic_environ, raw_data)
        assert result["user"] == "alice"

    def test_benchmark_parse_headers(self, benchmark, basic_environ):
        """Benchmark: Parsing HTTP headers."""
        basic_environ["HTTP_USER_AGENT"] = "Mozilla/5.0"
        basic_environ["HTTP_ACCEPT"] = "application/json"
        basic_environ["HTTP_AUTHORIZATION"] = "Bearer token123"
        basic_environ["HTTP_CONTENT_TYPE"] = "application/json"

        result = benchmark(HeaderParser.get_headers, basic_environ)
        assert len(result) >= 4

    def test_benchmark_urlencoded_parsing(self, benchmark, basic_environ):
        """Benchmark: Parsing urlencoded data."""
        raw_data = b"username=john&password=secret&email=john@example.com&age=25"

        basic_environ["CONTENT_TYPE"] = "application/x-www-form-urlencoded"

        result = benchmark(ParseBody.get_request_params, basic_environ, raw_data)
        assert "username" in result


# ============================================================================
# Templator Benchmarks
# ============================================================================


@pytest.mark.benchmark
class TestTemplatorBenchmarks:
    """Template engine performance benchmarks."""

    def test_benchmark_simple_template_render(self, benchmark, sample_template):
        """Benchmark: Rendering simple template."""
        templator = Templator(folder=str(sample_template))
        context = {"title": "Test", "heading": "Hello", "content": "World"}

        result = benchmark(templator.render, "test.html", content=context)
        assert "Test" in result

    def test_benchmark_template_with_loop(self, benchmark, temp_template_dir):
        """Benchmark: Rendering template with loop."""
        template_content = """
        <ul>
        {% for item in items %}
            <li>{{ item.name }} - {{ item.value }}</li>
        {% endfor %}
        </ul>
        """
        (temp_template_dir / "loop.html").write_text(template_content)

        templator = Templator(folder=str(temp_template_dir))
        items = [{"name": f"Item {i}", "value": i} for i in range(50)]

        result = benchmark(templator.render, "loop.html", items=items)
        assert "Item 0" in result


# ============================================================================
# Wiverno Application Benchmarks
# ============================================================================


@pytest.mark.benchmark
@pytest.mark.slow
class TestWivernoBenchmarks:
    """Complete request processing cycle benchmarks."""

    def test_benchmark_wsgi_call(self, benchmark, app_with_routes, environ_factory):
        """Benchmark: Full WSGI application call."""
        environ = environ_factory(method="GET", path="/")

        def wsgi_call():
            response_status = []
            response_headers = []

            def start_response(status, headers):
                response_status.append(status)
                response_headers.append(headers)

            body_iter = app_with_routes(environ, start_response)
            body = b"".join(body_iter)
            return response_status[0], body

        status, body = benchmark(wsgi_call)
        assert "200" in status

    def test_benchmark_route_matching(self, benchmark):
        """Benchmark: Route matching."""
        app = Wiverno()

        # Create many routes using the route decorator
        for i in range(100):

            @app.route(f"/route{i}")
            def handler(req, route_num=i):
                return ("200 OK", f"Route {route_num}")

        # Find route in the middle
        def find_route():
            for route_path, route_data in app._routes.items():
                if route_path == "/route50":
                    return route_data
            return None

        result = benchmark(find_route)
        assert result is not None

    def test_benchmark_app_initialization(self, benchmark):
        """Benchmark: Application initialization."""

        def init_app():
            app = Wiverno(debug_mode=True)

            @app.get("/")
            def home(request):
                return "200 OK", "Home"

            @app.get("/users")
            def users(request):
                return "200 OK", "Users"

            return app

        app = benchmark(init_app)
        assert len(app._routes) == 2


# ============================================================================
# Comparative Benchmarks
# ============================================================================


@pytest.mark.benchmark
class TestComparativeBenchmarks:
    """Comparative benchmarks for different approaches."""

    def test_benchmark_dict_lookup_vs_list_iteration(self, benchmark):
        """Benchmark: Comparing dict vs list lookup."""
        # This is a demonstration test for performance comparison

        routes_dict = {f"/route{i}": {"handler": lambda: "OK"} for i in range(1000)}

        def dict_lookup():
            return routes_dict.get("/route500")

        result = benchmark(dict_lookup)
        assert result is not None

    def test_benchmark_json_dumps(self, benchmark):
        """Benchmark: JSON serialization."""
        data = {
            "users": [
                {"id": i, "name": f"User{i}", "email": f"user{i}@example.com"} for i in range(100)
            ]
        }

        result = benchmark(json.dumps, data)
        assert "User0" in result

    def test_benchmark_json_loads(self, benchmark):
        """Benchmark: JSON deserialization."""
        json_str = json.dumps(
            {
                "users": [
                    {"id": i, "name": f"User{i}", "email": f"user{i}@example.com"}
                    for i in range(100)
                ]
            }
        )

        result = benchmark(json.loads, json_str)
        assert len(result["users"]) == 100


# ============================================================================
# Stress Tests
# ============================================================================


@pytest.mark.benchmark
@pytest.mark.slow
class TestStressBenchmarks:
    """Stress tests for performance under load."""

    def test_benchmark_many_requests(self, benchmark, app_with_routes, environ_factory):
        """Benchmark: Processing many requests."""

        def process_requests():
            results = []
            response_status: list[str] = []
            response_headers: list[list[tuple[str, str]]] = []

            def start_response(status: str, headers: list[tuple[str, str]]) -> None:
                response_status.append(status)
                response_headers.append(headers)

            for _i in range(100):
                environ = environ_factory(method="GET", path="/")
                response_status.clear()
                response_headers.clear()

                body_iter = app_with_routes(environ, start_response)
                body = b"".join(body_iter)
                results.append((response_status[0], body))

            return results

        results = benchmark(process_requests)
        assert len(results) == 100

    def test_benchmark_large_template_data(self, benchmark, temp_template_dir):
        """Benchmark: Rendering with large amount of data."""
        template_content = """
        {% for user in users %}
            <div>{{ user.id }}: {{ user.name }} - {{ user.email }}</div>
        {% endfor %}
        """
        (temp_template_dir / "large.html").write_text(template_content)

        templator = Templator(folder=str(temp_template_dir))
        users = [
            {"id": i, "name": f"User{i}", "email": f"user{i}@example.com"} for i in range(1000)
        ]

        result = benchmark(templator.render, "large.html", users=users)
        assert "User0" in result
        assert "User999" in result
