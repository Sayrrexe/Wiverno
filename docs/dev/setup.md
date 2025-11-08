# Development Setup

## Prerequisites

- Python 3.12+
- Git
- uv (recommended)

## Installation

Install Python 3.12+:

```bash
python --version
```

Install uv:

```bash
# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Clone and setup:

```bash
git clone https://github.com/YOUR_USERNAME/Wiverno.git
cd Wiverno
uv venv
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows
uv pip install -e ".[dev]"
pre-commit install
```

## Verify Installation

```bash
uv run pytest
uv run ruff check .
uv run mypy wiverno
```

## Main Commands

```bash
make dev              # Install dev dependencies
make test             # Run tests
make coverage         # Tests with coverage
make format           # Format code
make lint             # Check code quality
make typecheck        # Type checking
make check            # All checks
make docs-serve       # Serve documentation
wiverno run dev app:app  # Dev server
```

## Development Server

```bash
wiverno run dev app:app
wiverno run dev app:app --host 0.0.0.0 --port 5000
```

## Next Steps

- [Testing](testing.md) - Writing tests
- [Code Style](code-style.md) - Code standards
- [Linting](linting.md) - Code quality
- [Type Hints](type-hints.md) - Type annotations
- [Architecture](architecture.md) - Understanding codebase
- [Contributing](contributing.md) - How to contribute
