# Testing

Comprehensive guide to testing in Wiverno.

## Running Tests

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/unit/test_router.py

# Run specific test
uv run pytest tests/unit/test_router.py::test_name

# Run with coverage
uv run pytest --cov=wiverno

# Generate HTML coverage report
uv run pytest --cov=wiverno --cov-report=html

# Run benchmarks
uv run pytest tests/benchmark/ --benchmark-only
```

## Test Structure

```
tests/
├── conftest.py          # Shared fixtures
├── unit/                # Unit tests
├── integration/         # Integration tests
└── benchmark/           # Performance tests
```

## Writing Tests

### Unit Test Example

```python
import pytest
from wiverno.core.router import Router

def test_basic_route_matching():
    """Test basic route matching works."""
    def view(request):
        return "200 OK", "test"

    router = Router([("/test", view)])
    handler, params = router.match("/test")

    assert handler is view
    assert params == {}
```

### Integration Test Example

```python
from wiverno.main import Wiverno

def test_full_request_cycle():
    """Test complete request-response cycle."""
    def index(request):
        return "200 OK", "Hello"

    app = Wiverno(routes_list=[("/", index)])

    environ = {
        "REQUEST_METHOD": "GET",
        "PATH_INFO": "/",
        "wsgi.url_scheme": "http",
        "SERVER_NAME": "localhost",
        "SERVER_PORT": "8000",
    }

    response_status = []
    def start_response(status, headers):
        response_status.append(status)

    response = app(environ, start_response)
    body = b"".join(response)

    assert response_status[0] == "200 OK"
    assert body == b"Hello"
```

### Benchmark Test Example

```python
import pytest
from wiverno.core.router import Router

def test_router_performance(benchmark):
    """Benchmark router matching speed."""
    routes = [(f"/route{i}", lambda r: ("200 OK", "")) for i in range(100)]
    router = Router(routes)

    def match_route():
        return router.match("/route50")

    result = benchmark(match_route)
    assert result[0] is not None
```

## WSGI Testing

Test WSGI applications directly:

```python
environ = {
    "REQUEST_METHOD": "GET",
    "PATH_INFO": "/",
    "QUERY_STRING": "",
    "wsgi.url_scheme": "http",
    "SERVER_NAME": "localhost",
    "SERVER_PORT": "8000",
}

response_status = []
def start_response(status, headers):
    response_status.append(status)

response = app(environ, start_response)
body = b"".join(response)
assert response_status[0] == "200 OK"
```

Test POST with JSON:

```python
import json

body = json.dumps({"name": "Alice"}).encode()
environ = {
    "REQUEST_METHOD": "POST",
    "PATH_INFO": "/users",
    "CONTENT_TYPE": "application/json",
    "CONTENT_LENGTH": str(len(body)),
    "wsgi.input": __import__("io").BytesIO(body),
    "wsgi.url_scheme": "http",
    "SERVER_NAME": "localhost",
    "SERVER_PORT": "8000",
}

response_status = []
def start_response(status, headers):
    response_status.append(status)

response = app(environ, start_response)
assert response_status[0] == "201 CREATED"
```

## conftest.py Example

Shared fixtures for all tests:

```python
import io
import pytest
from wiverno.core.requests import Request
from wiverno.main import Wiverno


@pytest.fixture
def basic_environ():
    """Minimal WSGI environment."""
    return {
        "REQUEST_METHOD": "GET",
        "PATH_INFO": "/",
        "QUERY_STRING": "",
        "CONTENT_TYPE": "",
        "CONTENT_LENGTH": "0",
        "wsgi.url_scheme": "http",
        "SERVER_NAME": "localhost",
        "SERVER_PORT": "8000",
        "HTTP_HOST": "localhost:8000",
    }


@pytest.fixture
def environ_factory():
    """Factory for creating WSGI environments."""
    def _create_environ(
        method="GET",
        path="/",
        body=b"",
        headers=None,
    ):
        environ = {
            "REQUEST_METHOD": method,
            "PATH_INFO": path,
            "CONTENT_LENGTH": str(len(body)),
            "wsgi.input": io.BytesIO(body),
            "wsgi.url_scheme": "http",
            "SERVER_NAME": "localhost",
            "SERVER_PORT": "8000",
        }
        if headers:
            for key, value in headers.items():
                wsgi_key = f"HTTP_{key.upper().replace('-', '_')}"
                environ[wsgi_key] = value
        return environ
    return _create_environ


@pytest.fixture
def app():
    """Fresh Wiverno application."""
    return Wiverno()
```

## Best Practices

Use descriptive test names: `test_router_matches_exact_path()`

Follow Arrange-Act-Assert pattern:

```python
def test_something():
    # Arrange - Setup
    router = Router([("/test", view)])

    # Act - Execute
    result = router.match("/test")

    # Assert - Verify
    assert result is not None
```

Use parametrize for multiple cases:

```python
@pytest.mark.parametrize("path,expected", [
    ("/", True),
    ("/about", True),
    ("/404", False),
])
def test_route_exists(path, expected):
    router = Router([("/", view), ("/about", view)])
    handler, _ = router.match(path)
    assert (handler is not None) == expected
```

## Debugging

Print debugging: `uv run pytest -s`

Using breakpoint: `import pdb; pdb.set_trace()`

Common flags:
- `-x` - Stop on first failure
- `-v` - Verbose output
- `-s` - Show print output
- `--lf` - Run last failed tests

## Pytest Configuration

Configuration in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
minversion = "8.0"
testpaths = ["tests"]
addopts = [
    "-ra",
    "--strict-markers",
    "--cov=wiverno",
    "--cov-report=term-missing",
    "--cov-fail-under=50",
]

markers = [
    "unit: unit tests",
    "integration: integration tests",
    "benchmark: performance tests",
]
```

Test markers:

```bash
uv run pytest -m unit          # Run only unit tests
uv run pytest -m integration   # Run only integration tests
uv run pytest -m "not slow"    # Skip slow tests
```

## Coverage

Coverage requirement: minimum 50%

```bash
# Generate HTML report
uv run pytest --cov=wiverno --cov-report=html

# View coverage
open htmlcov/index.html
```

## Next Steps

- [Code Style](code-style.md) - Code standards
- [Linting](linting.md) - Code quality
- [Type Hints](type-hints.md) - Type annotations
- [Architecture](architecture.md) - Understanding codebase
- [Contributing](contributing.md) - How to contribute
