# Type Hints

Type annotation requirements for Wiverno.

## MyPy Strict Mode

Enabled in `pyproject.toml`:

```toml
[tool.mypy]
python_version = "3.12"
warn_return_any = true
disallow_untyped_defs = true
check_untyped_defs = true
```

All functions must have complete type annotations.

## Core Rules

1. **All functions require types:** Parameters and return values
2. **Use modern syntax:** `list[str]` not `List[str]`
3. **Union types with `|`:** `int | None` not `Optional[int]`
4. **No `Any` type:** Use specific types or TypeVar
5. **Generic classes:** Use TypeVar for reusable components
6. **Accurate returns:** Match actual return values

## Common Patterns

Basic function:

```python
def add(a: int, b: int) -> int:
    return a + b
```

Optional return:

```python
def find_item(items: list[str], name: str) -> str | None:
    for item in items:
        if item == name:
            return item
    return None
```

Complex types:

```python
from typing import TypeVar, Generic

T = TypeVar("T")

def process(data: dict[str, list[int]]) -> list[str]:
    return list(data.keys())

class Container(Generic[T]):
    def __init__(self, value: T) -> None:
        self.value = value

    def get(self) -> T:
        return self.value
```

## Wiverno Types

Request handling:

```python
from wiverno.core.requests import Request
from wiverno.main import Wiverno

def handler(request: Request) -> tuple[str, str]:
    return "200 OK", "response body"

def setup_app(app: Wiverno) -> None:
    @app.get("/")
    def index(request: Request) -> tuple[str, str]:
        return "200 OK", "Home"
```

WSGI types:

```python
from typing import Callable

# WSGI environ dict
environ: dict[str, str]

# WSGI start_response callable
StartResponse = Callable[[str, list[tuple[str, str]]], None]

# WSGI application signature
def app(environ: dict[str, str], start_response: StartResponse) -> list[bytes]:
    pass
```

## Checking

Run mypy:

```bash
uv run mypy wiverno
```

Fix type errors:

```bash
uv run mypy --show-error-codes wiverno
uv run mypy wiverno/core/router.py  # Check specific file
```

## Next Steps

- [Code Style](code-style.md) - Code standards
- [Linting](linting.md) - Code quality tools
- [Testing](testing.md) - Writing tests
- [Contributing](contributing.md) - Contribution guidelines
