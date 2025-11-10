# Development Guide

Welcome to Wiverno development documentation!

## Quick Start

1. Fork: https://github.com/Sayrrexe/Wiverno
2. Clone: `git clone https://github.com/YOUR_USERNAME/Wiverno.git`
3. Setup: `uv pip install -e ".[dev]"`
4. Pre-commit: `pre-commit install`
5. Branch: `git checkout -b feature/name`
6. Develop: `make check` to verify code
7. Commit: `git commit -m "feat: description"`
8. PR: Push and create pull request

## Main Sections

**Getting Started**
- [Contributing](contributing.md) - How to contribute
- [Setup](setup.md) - Development environment

**Code Quality**
- [Code Style](code-style.md) - Naming, organization, docstrings
- [Type Hints](type-hints.md) - Type annotation rules
- [Linting](linting.md) - Ruff, MyPy, pre-commit

**Testing & Performance**
- [Testing](testing.md) - Running tests, fixtures, examples
- [Benchmarks](benchmarks.md) - Performance testing, profiling, optimization

**Understanding Wiverno**
- [Architecture](architecture.md) - How Wiverno works
- [Project Structure](project-structure.md) - File organization
- [Workflow](workflow.md) - Development process

## Common Commands

```bash
make test              # Run tests
make format            # Format code
make lint              # Check code quality
make typecheck         # Type check
make check             # All checks
make docs-serve        # Serve documentation
wiverno run dev app:app  # Dev server with auto-reload
```

## Requirements

- Python 3.12+
- All functions must have type hints
- Tests for new code
- Code formatted and linted
- Coverage > 50%

## Tools

- **Ruff** - Linter and formatter
- **MyPy** - Type checker (strict mode)
- **Pytest** - Testing framework
- **Pre-commit** - Automated checks
- **uv** - Package manager
- **Make** - Task automation

## Project Layout

```
wiverno/              Main package
├── core/             Requests, router, server
├── templating/       Template engine
├── views/            View classes
├── dev/              Dev tools
├── main.py           WSGI app
└── cli.py            CLI interface

tests/                Test suite
├── unit/             Unit tests
├── integration/      Integration tests
└── benchmark/        Performance tests

docs/                 Documentation
├── api/              API reference
├── dev/              Developer docs
└── guide/            User guides
```

## PR Checklist

- Tests pass: `uv run pytest`
- Coverage > 50%
- Code formatted: `uv run ruff format .`
- No lint errors: `uv run ruff check .`
- Types checked: `uv run mypy wiverno`
- Tests added for new code
- Commit messages clear

## Get Help

- [GitHub Issues](https://github.com/Sayrrexe/Wiverno/issues) - Report bugs
- [GitHub Discussions](https://github.com/Sayrrexe/Wiverno/discussions) - Ask questions

## Next Steps

- [Contributing](contributing.md) - Detailed guidelines
- [Architecture](architecture.md) - How Wiverno works
- [Testing](testing.md) - Writing tests
