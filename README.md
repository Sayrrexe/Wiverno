# Wiverno

**Wiverno** — a lightweight WSGI framework for building fast and flexible Python web applications.

## Installation

Clone the repository and install the package using `pip`:

```bash
pip install .
```

## Development Setup

For contributors and developers:

1. **Install with development dependencies**:

   ```bash
   pip install -e ".[dev]"
   # or using uv:
   uv sync --all-extras
   ```

2. **Install pre-commit hooks**:

   ```bash
   uv run pre-commit install
   ```

   This will automatically run code quality checks before each commit. See [Pre-commit Hooks Guide](docs/dev/pre-commit.md) for details.

## Minimal example

```python
from wiverno import Wiverno

app = Wiverno()

@app.get("/")
def index(request):
    return "200 OK", "Hello, World!"
```

## Running

Save the example above to `run.py` and start the development server:

```bash
wiverno run dev
```

The application will be available at `http://localhost:8000/`.
