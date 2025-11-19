# Linting and Code Quality

Code quality tools and commands for Wiverno.

## Ruff

Fast Python linter and formatter.

### Commands

```bash
uv run ruff check .              # Check for issues
uv run ruff check --fix .        # Fix automatically
uv run ruff format .             # Format code
uv run ruff check wiverno/core/  # Check specific folder
```

### Rules

| Code | Rule                            |
| ---- | ------------------------------- |
| E    | pycodestyle errors              |
| W    | pycodestyle warnings            |
| F    | pyflakes (undefined names, etc) |
| I    | isort (import sorting)          |
| B    | flake8-bugbear (common bugs)    |
| C4   | flake8-comprehensions           |
| UP   | pyupgrade (modern syntax)       |
| S    | flake8-bandit (security)        |

Configuration: `pyproject.toml` - line-length: 100 characters, Python 3.12 target

## MyPy

Static type checker for strict mode enforcement.

### Commands

```bash
uv run mypy wiverno              # Check all files
uv run mypy wiverno/core/routing/router.py  # Check specific file
uv run mypy --show-error-codes wiverno  # Show error codes
```

Configuration: `pyproject.toml` - strict mode enabled

## Pre-commit

Git hooks for automated checks before commits.

### Setup

```bash
pre-commit install              # Install hooks
pre-commit run --all-files      # Run on all files
pre-commit autoupdate           # Update to latest
```

Checks:

1. Ruff linting
2. Ruff formatting
3. MyPy type checking
4. Trailing whitespace
5. End of file newline

## Quick Checklist

Before commit:

```bash
uv run ruff format .           # Format
uv run ruff check .            # Lint
uv run mypy wiverno            # Type check
uv run pytest                  # Tests
```

## Common Fixes

Import sorting (Ruff I):

```python
# Good order: __future__, stdlib, third-party, local
from __future__ import annotations
import os
from jinja2 import Environment
from wiverno.core.routing import router
```

Line length (E501) - max 100 chars:

```python
# Break long lines
result = some_function(
    arg1, arg2, arg3,
)
```

Unused imports (F401):

```python
# Remove unused imports
from pathlib import Path  # Good - used
# from os import environ  # Bad - unused
```

Type annotations (ANN):

```python
# Always type functions
def process(data: dict[str, str]) -> list[str]:
    return list(data.keys())
```

## Next Steps

- [Code Style](code-style.md) - Code standards
- [Type Hints](type-hints.md) - Type annotations
- [Testing](testing.md) - Writing tests
- [Contributing](contributing.md) - Contribution guidelines
