# Code Style Guide

Code standards for Wiverno development.

## Naming Conventions

| Item            | Convention            | Example              |
| --------------- | --------------------- | -------------------- |
| Module/File     | snake_case            | `request_parser.py`  |
| Class           | PascalCase            | `RequestParser`      |
| Function/Method | snake_case            | `parse_request()`    |
| Constant        | UPPER_SNAKE_CASE      | `MAX_SIZE = 1000`    |
| Private         | \_leading_underscore  | `_internal_method()` |
| Magic           | \_\_double_underscore | `__init__()`         |

## Type Hints

Always add type hints (required by mypy strict mode):

```python
# Good - Full types
def process_data(data: dict[str, str]) -> list[str]:
    return list(data.keys())

# Good - Union types with |
def get_value(key: str) -> int | None:
    return None

# Good - Complex types
from typing import TypeVar
T = TypeVar("T")
def container(value: T) -> T:
    return value
```

Wiverno-specific types:

```python
from wiverno.core.requests import Request
from wiverno.main import Wiverno

def handler(request: Request) -> tuple[str, str]:
    return "response"

def app_setup(app: Wiverno) -> None:
    @app.get("/")
    def index(request: Request) -> tuple[str, str]:
        return "Home"
```

## Docstrings

Use Google style docstrings:

```python
def process_request(request: Request, timeout: int = 30) -> tuple[str, str]:
    """Process an incoming HTTP request.

    Args:
        request: The HTTP request object.
        timeout: Request timeout in seconds.

    Returns:
        Tuple of (status_code, response_body).
    """
    return "processed"
```

## Import Organization

```python
from __future__ import annotations

import os
from io import BytesIO
from typing import TypeVar

from jinja2 import Environment

from wiverno.core.requests import Request
from wiverno.main import Wiverno
```

Order: `__future__`, standard library, third-party, local imports

## File Organization

```python
"""Module docstring."""

import required_modules
from relative_imports import something

# Constants
MAX_SIZE = 1000

# Type variables
T = TypeVar("T")

# Classes
class MyClass:
    pass

# Functions
def my_function() -> None:
    pass

# Main block
if __name__ == "__main__":
    pass
```

## Comments

Use comments sparingly - prefer clear code:

```python
# Bad - Obvious comment
x = 1  # Set x to 1

# Good - Explains why
cached_routes = {}  # Cache for O(1) route lookup instead of O(n)
```

## Error Handling

```python
# Good - Specific exceptions
try:
    data = json.loads(body)
except json.JSONDecodeError as e:
    raise ValueError(f"Invalid JSON: {e}") from e

# Bad - Too broad
try:
    data = json.loads(body)
except Exception:
    pass
```

## Code Quality Targets

- **Line length:** < 100 characters (enforced by Ruff)
- **Type coverage:** 100% (enforced by mypy strict)
- **Complexity:** Keep functions simple and focused
- **Duplication:** DRY principle - don't repeat code

## Next Steps

- [Linting](linting.md) - Code quality tools
- [Type Hints](type-hints.md) - Detailed type annotations
- [Testing](testing.md) - Writing tests
- [Contributing](contributing.md) - Contribution guidelines
