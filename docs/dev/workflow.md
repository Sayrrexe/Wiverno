# Development Workflow

Development process for Wiverno.

## Steps

1. **Write code** - Create features/fix bugs
2. **Test** - `uv run pytest` (>50% coverage required)
3. **Format** - `uv run ruff format .`
4. **Lint** - `uv run ruff check .`
5. **Type check** - `uv run mypy wiverno`
6. **Commit** - `git commit` (pre-commit hooks run)
7. **Push** - `git push`
8. **Pull request** - Create PR on GitHub

## Quick Commands

```bash
make test            # Run tests
make format          # Format code
make lint            # Check code quality
make typecheck       # Type checking
make check           # All checks (format + lint + typecheck + test)
```

## Pre-commit Flow

When you run `git commit`:

1. Ruff linting
2. Ruff formatting
3. MyPy type checking
4. Trailing whitespace removal
5. EOF newline check

If any check fails, fix it and commit again.

## Development Server

```bash
wiverno run dev app:app              # Start server
wiverno run dev app:app --port 5000  # Custom port
```

Auto-reload on code changes.

## Testing During Development

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test
uv run pytest tests/unit/test_router.py::test_name

# Run and stop on first failure
uv run pytest -x

# Run only unit tests
uv run pytest -m unit

# Generate coverage report
uv run pytest --cov=wiverno --cov-report=html
```

## Common Tasks

### Adding a New Feature

1. Create feature branch: `git checkout -b feature/name`
2. Write code with tests
3. Run checks: `make check`
4. Commit: `git commit -m "feat: description"`
5. Push and create PR

### Fixing a Bug

1. Create fix branch: `git checkout -b fix/name`
2. Write failing test
3. Fix code
4. Run checks: `make check`
5. Commit: `git commit -m "fix: description"`
6. Push and create PR

### Running All Checks

```bash
make check
```

Runs:
- Format check
- Linting
- Type checking
- Tests (with coverage)

## Next Steps

- [Testing](testing.md) - Writing tests
- [Code Style](code-style.md) - Code standards
- [Linting](linting.md) - Code quality
- [Contributing](contributing.md) - Contribution guidelines
