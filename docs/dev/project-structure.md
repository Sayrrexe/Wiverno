# Project Structure

File organization in Wiverno.

## Directory Tree

```
Wiverno/
├── .github/               # GitHub Actions workflows
├── docs/                  # Documentation
│   ├── api/              # API reference
│   ├── dev/              # Developer docs
│   └── guide/            # User guides
├── tests/                # Test suite
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── benchmark/        # Performance tests
├── wiverno/              # Main package
│   ├── core/             # Core functionality
│   ├── dev/              # Development tools
│   ├── static/           # Static assets
│   ├── templating/       # Template engine
│   ├── views/            # View classes
│   └── __init__.py
├── .gitignore
├── .pre-commit-config.yaml
├── Makefile
├── LICENSE
├── README.md
├── mkdocs.yml            # Documentation config
└── pyproject.toml        # Project config
```

## Modules

### wiverno/core/

Core framework functionality:

| File | Purpose |
|------|---------|
| `requests.py` | Request parsing and handling |
| `router.py` | Route matching and registration |
| `server.py` | WSGI server wrapper |

### wiverno/templating/

Template rendering:

| File | Purpose |
|------|---------|
| `templator.py` | Jinja2 template wrapper |

### wiverno/views/

View classes and error handlers:

| File | Purpose |
|------|---------|
| `base_views.py` | BaseView class-based views |
| `pages_errors.py` | Default 404/405/500 handlers |

### wiverno/dev/

Development utilities:

| File | Purpose |
|------|---------|
| `dev_server.py` | Dev server with hot reload |

### Root Level

| File | Purpose |
|------|---------|
| `main.py` | Wiverno WSGI application |
| `cli.py` | CLI interface (Typer-based) |

### tests/

Test organization:

- `unit/` - Fast isolated tests
- `integration/` - Multi-component tests
- `benchmark/` - Performance tests
- `conftest.py` - Shared test fixtures

## Key Files

| File | Purpose |
|------|---------|
| `pyproject.toml` | Dependencies, config, tools |
| `mkdocs.yml` | Documentation configuration |
| `.pre-commit-config.yaml` | Pre-commit hooks |
| `Makefile` | Development commands |
| `README.md` | Project overview |

## Next Steps

- [Architecture](architecture.md) - Component details
- [Testing](testing.md) - Writing tests
- [Workflow](workflow.md) - Development process
- [Contributing](contributing.md) - How to contribute
