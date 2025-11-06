# Wiverno Tests

Comprehensive testing infrastructure for the Wiverno framework.


## Quick Start

### Installing Dependencies

```powershell
uv pip install -e ".[dev]"

# Or via pip
pip install -e ".[dev]"
```

### Running All Tests

```powershell
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=wiverno --cov-report=html
```

## Running Different Types of Tests

### Unit Tests

```powershell
# Only unit tests (fast)
pytest -m unit

# Specific file
pytest tests/unit/test_router.py

# Specific test
pytest tests/unit/test_router.py::TestRouterInitialization::test_router_initialization
```

### Integration Tests

```powershell
# Only integration tests
pytest -m integration

# Exclude integration tests
pytest -m "not integration"
```

### Performance Tests

```powershell
# Only benchmarks
pytest -m benchmark --benchmark-only

# Benchmarks with auto-save
pytest tests/benchmark/ --benchmark-autosave

# Compare with previous results
pytest tests/benchmark/ --benchmark-compare

# Detailed benchmark report
pytest tests/benchmark/ --benchmark-verbose
```

### Slow Tests

```powershell
# Skip slow tests
pytest -m "not slow"

# Only slow tests
pytest -m slow
```

## Code Coverage

### Generating Coverage Reports

```powershell
# HTML report (will open in browser)
pytest --cov=wiverno --cov-report=html
start htmlcov/index.html

# Terminal report
pytest --cov=wiverno --cov-report=term-missing

# XML report (for CI/CD)
pytest --cov=wiverno --cov-report=xml
```

### Coverage Requirements

- **Minimum coverage**: 50%
- Configured in `pyproject.toml`: `--cov-fail-under=90`

## Test Markers

Available markers for filtering tests:

| Marker        | Description              | Example Usage           |
| ------------- | ------------------------ | ----------------------- |
| `unit`        | Fast isolated unit tests | `pytest -m unit`        |
| `integration` | Integration tests        | `pytest -m integration` |
| `slow`        | Slow tests               | `pytest -m "not slow"`  |
| `benchmark`   | Performance tests        | `pytest -m benchmark`   |

### Combining Markers

```powershell
# Unit tests, but not slow
pytest -m "unit and not slow"

# Integration or benchmarks
pytest -m "integration or benchmark"
```

## Fixtures

### Main Fixtures (from `conftest.py`)

#### WSGI Environment

- `basic_environ` - basic WSGI environment.
- `environ_factory` - factory for creating custom environments.

```python
def test_example(environ_factory):
    environ = environ_factory(method="POST", path="/api/users")
    # ...
```

#### Router

- `router` - clean instance of Router.
- `router_with_routes` - Router with pre-set routes.

#### Wiverno Application

- `app` - clean application.
- `app_with_routes` - application with test routes.

#### Request

- `request_factory` - factory for creating Request objects.

#### Templates

- `temp_template_dir` - temporary directory for templates.
- `sample_template` - ready-to-use test template.

#### Utilities

- `call_wsgi_app` - utility for calling WSGI applications.

