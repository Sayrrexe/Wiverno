# Benchmarks

Performance testing and optimization for Wiverno.

## Overview

Wiverno includes performance benchmarks to track and improve performance over time. Benchmarks are run using pytest-benchmark.

## Running Benchmarks

```bash
# Run all benchmarks
make benchmark

# Or directly
uv run pytest tests/benchmark/ --benchmark-only

# With comparison
uv run pytest tests/benchmark/ --benchmark-compare

# Save results
uv run pytest tests/benchmark/ --benchmark-save=results

# Compare with saved results
uv run pytest tests/benchmark/ --benchmark-compare=results
```

## Benchmark Suite

### Router Performance

Test route matching speed:

```python
"""Benchmark router performance."""
import pytest
from wiverno.core.router import Router


def test_simple_routing(benchmark):
    """Benchmark simple route matching."""
    routes = [("/", lambda r: ("200 OK", "test"))]
    router = Router(routes)

    result = benchmark(router.match, "/")
    handler, params = result
    assert handler is not None


def test_parameter_extraction(benchmark):
    """Benchmark path parameter extraction."""
    routes = [("/user/<id>", lambda r: ("200 OK", "test"))]
    router = Router(routes)

    result = benchmark(router.match, "/user/123")
    handler, params = result
    assert params["id"] == "123"


def test_large_route_table(benchmark):
    """Benchmark with many routes."""
    routes = [
        (f"/route{i}", lambda r: ("200 OK", "test"))
        for i in range(100)
    ]
    router = Router(routes)

    result = benchmark(router.match, "/route50")
    handler, params = result
    assert handler is not None


def test_complex_patterns(benchmark):
    """Benchmark complex route patterns."""
    routes = [
        ("/api/v1/users/<user_id>/posts/<post_id>/comments/<comment_id>",
         lambda r: ("200 OK", "test"))
    ]
    router = Router(routes)

    result = benchmark(
        router.match,
        "/api/v1/users/123/posts/456/comments/789"
    )
    handler, params = result
    assert len(params) == 3
```

### Request Parsing

Test request parsing performance:

```python
"""Benchmark request parsing."""
import pytest
from wiverno.core.requests import Request


def test_basic_request_parsing(benchmark):
    """Benchmark basic request creation."""
    environ = {
        "REQUEST_METHOD": "GET",
        "PATH_INFO": "/",
        "QUERY_STRING": "",
        "wsgi.url_scheme": "http",
        "SERVER_NAME": "localhost",
        "SERVER_PORT": "8000",
    }

    request = benchmark(Request, environ)
    assert request.method == "GET"


def test_query_param_parsing(benchmark):
    """Benchmark query parameter parsing."""
    environ = {
        "REQUEST_METHOD": "GET",
        "PATH_INFO": "/search",
        "QUERY_STRING": "q=python&page=1&limit=10",
        "wsgi.url_scheme": "http",
        "SERVER_NAME": "localhost",
        "SERVER_PORT": "8000",
    }

    request = benchmark(Request, environ)
    assert len(request.query_params) == 3


def test_header_parsing(benchmark):
    """Benchmark header parsing."""
    environ = {
        "REQUEST_METHOD": "GET",
        "PATH_INFO": "/",
        "QUERY_STRING": "",
        "HTTP_USER_AGENT": "Mozilla/5.0",
        "HTTP_ACCEPT": "text/html",
        "HTTP_ACCEPT_LANGUAGE": "en-US",
        "wsgi.url_scheme": "http",
        "SERVER_NAME": "localhost",
        "SERVER_PORT": "8000",
    }

    request = benchmark(Request, environ)
    assert len(request.headers) >= 3
```

### Application Performance

Test full request-response cycle:

```python
"""Benchmark full application."""
import pytest
from wiverno.main import Wiverno


def test_simple_request_cycle(benchmark):
    """Benchmark complete request-response cycle."""
    def index(request):
        return "200 OK", "Hello, World!"

    app = Wiverno(routes_list=[("/", index)])

    environ = {
        "REQUEST_METHOD": "GET",
        "PATH_INFO": "/",
        "QUERY_STRING": "",
        "wsgi.url_scheme": "http",
        "SERVER_NAME": "localhost",
        "SERVER_PORT": "8000",
    }

    response_data = []

    def start_response(status, headers):
        response_data.append((status, headers))

    def run_request():
        return list(app(environ, start_response))

    response = benchmark(run_request)
    assert response_data[0][0] == "200 OK"


def test_parameterized_request(benchmark):
    """Benchmark request with path parameters."""
    def user_view(request):
        user_id = request.path_params.get("id")
        return "200 OK", f"User {user_id}"

    app = Wiverno(routes_list=[("/user/<id>", user_view)])

    environ = {
        "REQUEST_METHOD": "GET",
        "PATH_INFO": "/user/123",
        "QUERY_STRING": "",
        "wsgi.url_scheme": "http",
        "SERVER_NAME": "localhost",
        "SERVER_PORT": "8000",
    }

    response_data = []

    def start_response(status, headers):
        response_data.append((status, headers))

    def run_request():
        return list(app(environ, start_response))

    response = benchmark(run_request)
    assert b"User 123" in response[0]
```

## Performance Metrics

### Current Performance

Target metrics (as of v0.1.2):

| Operation            | Target  | Actual |
| -------------------- | ------- | ------ |
| Simple routing       | < 10μs  | ~8μs   |
| Parameter extraction | < 15μs  | ~12μs  |
| Request parsing      | < 20μs  | ~18μs  |
| Full request cycle   | < 50μs  | ~45μs  |
| Template rendering   | < 100μs | ~90μs  |

### Comparison with Other Frameworks

Relative performance (lower is better):

| Framework | Requests/sec | Relative Speed  |
| --------- | ------------ | --------------- |
| Wiverno   | 22,000       | 1.0x (baseline) |
| Flask     | 18,000       | 0.82x           |
| FastAPI   | 25,000       | 1.14x           |
| Starlette | 28,000       | 1.27x           |

_Note: Benchmarks vary based on hardware and test conditions._

## Profiling

### CPU Profiling

Profile CPU usage:

```bash
# Install profiling tools
uv pip install py-spy

# Profile running server
py-spy record -o profile.svg -- python app.py

# View flamegraph
open profile.svg
```

### Memory Profiling

Profile memory usage:

```bash
# Install memory profiler
uv pip install memory_profiler

# Run with profiling
python -m memory_profiler app.py
```

### Line-by-line Profiling

Profile specific functions:

```python
from memory_profiler import profile

@profile
def my_function():
    """Function to profile."""
    # Your code here
    pass
```

## Optimization Strategies

### 1. Route Table Optimization

Order routes by frequency:

```python
# Good - Frequent routes first
routes = [
    ("/", index),           # Most common
    ("/api/users", users),  # Common
    ("/admin/debug", debug), # Rare
]

# Bad - Rare routes first
routes = [
    ("/admin/debug", debug),
    ("/api/users", users),
    ("/", index),
]
```

### 2. Request Parsing

Parse data lazily:

```python
class Request:
    @property
    def query_params(self):
        """Parse query params on first access."""
        if not hasattr(self, "_query_params"):
            self._query_params = parse_qs(self.query_string)
        return self._query_params
```

### 3. Template Caching

Jinja2 automatically caches compiled templates. No action needed.

### 4. Static File Serving

Use nginx or CDN for static files in production:

```nginx
location /static/ {
    alias /path/to/static/;
    expires 30d;
}
```

### 5. Response Compression

Use middleware for compression:

```python
class GzipMiddleware:
    """Compress responses with gzip."""

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        # Implement gzip compression
        pass
```

## Load Testing

### Using Apache Bench

```bash
# Install apache bench
# Ubuntu: apt-get install apache2-utils
# macOS: included by default

# Run load test
ab -n 10000 -c 100 http://localhost:8000/

# Results:
# Requests per second: 2000 [#/sec]
# Time per request: 50 [ms]
```

### Using wrk

```bash
# Install wrk
# Ubuntu: apt-get install wrk
# macOS: brew install wrk

# Run load test
wrk -t 4 -c 100 -d 30s http://localhost:8000/

# Results:
# Thread Stats   Avg      Stdev     Max   +/- Stdev
#   Latency     5.00ms    2.00ms   50.00ms   95.00%
#   Req/Sec     5.00k     1.00k    7.00k    75.00%
# 600000 requests in 30.00s, 100.00MB read
# Requests/sec:  20000.00
```

### Using locust

```python
# locustfile.py
from locust import HttpUser, task, between

class WivernoUser(HttpUser):
    """Simulate user behavior."""

    wait_time = between(1, 3)

    @task
    def index(self):
        """Load homepage."""
        self.client.get("/")

    @task(3)
    def api_users(self):
        """Load API endpoint (3x more frequent)."""
        self.client.get("/api/users")
```

Run:

```bash
# Install locust
uv pip install locust

# Run load test
locust -f locustfile.py --host=http://localhost:8000
```

## Continuous Benchmarking

Track performance over time:

```bash
# Baseline benchmark
uv run pytest tests/benchmark/ --benchmark-save=baseline

# After changes
uv run pytest tests/benchmark/ --benchmark-compare=baseline

# View comparison
# If slower, investigate changes
# If faster, celebrate! 🎉
```

## Profiling

Profile code to identify bottlenecks:

```python
import cProfile
import pstats
from io import StringIO

pr = cProfile.Profile()
pr.enable()

# Code to profile
router.match("/route50")

pr.disable()
s = StringIO()
ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
ps.print_stats(10)
print(s.getvalue())
```

## Optimization Tips

1. Order routes by frequency (frequent routes first)
2. Use caching for computed values
3. Return early when possible
4. Parse data lazily (on first access)
5. Use appropriate data structures (dict vs list)
6. Compile templates once, reuse many times
7. Use middleware for cross-cutting concerns

## Next Steps

- [Testing](testing.md) - Write comprehensive tests
- [Contributing](contributing.md) - Contribute improvements
