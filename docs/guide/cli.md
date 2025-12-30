# CLI Commands

Complete guide to Wiverno's command-line interface.

## Overview

Wiverno provides a powerful CLI for managing your application development, testing, and deployment. All commands are available through the `wiverno` command.

## Quick Reference

```bash
wiverno run dev              # Start development server
wiverno run prod             # Start production server
wiverno docs                 # Serve documentation
wiverno help                 # Show help
```

## Server Commands

### Development Server

Start a development server with hot reload:

```bash
# Basic usage
wiverno run dev

# Custom port
wiverno run dev --port 3000

# Custom host (listen on all interfaces)
wiverno run dev --host 0.0.0.0

# Custom app location
wiverno run dev --app-module myapp --app-name application

# Watch specific directories
wiverno run dev --watch src,lib
```

**Options:**

- `--host, -h` - Server host address (default: `localhost`)
- `--port, -p` - Server port number (default: `8000`)
- `--app-module, -m` - Module containing the WSGI app (default: `run`)
- `--app-name, -a` - Name of the app variable (default: `app`)
- `--watch, -w` - Comma-separated directories to watch

**Example:**

```bash
# run.py
from wiverno.main import Wiverno

app = Wiverno()

@app.get("/")
def index(request):
    return "Hello, World!"
```

Run:

```bash
wiverno run dev
```

The server will automatically reload when you modify Python files.

### Production Server

Start a production server without hot reload:

```bash
# Basic usage
wiverno run prod

# Custom configuration
wiverno run prod --host 0.0.0.0 --port 8080

# Custom app location
wiverno run prod --app-module myapp --app-name application
```

**Options:**

- `--host, -h` - Server host address (default: `localhost`)
- `--port, -p` - Server port number (default: `8000`)
- `--app-module, -m` - Module containing the WSGI app (default: `run`)
- `--app-name, -a` - Name of the app variable (default: `app`)

**Note:** For production deployment, consider using a production WSGI server like:

- Gunicorn: `gunicorn app:app`
- uWSGI: `uwsgi --http :8000 --wsgi-file app.py --callable app`
- Waitress: `waitress-serve --port=8000 app:app`

## Documentation Commands

### Serve Documentation

Start a documentation server with live reload:

```bash
# Default (opens in browser)
wiverno docs

# Custom port
wiverno docs --port 3000

# Custom host
wiverno docs --host 0.0.0.0

# Don't open browser
wiverno docs --no-open
```

**Options:**

- `--host, -h` - Documentation server host (default: `127.0.0.1`)
- `--port, -p` - Documentation server port (default: `8000`)
- `--open/--no-open` - Open browser automatically (default: `True`)

**Example:**

```bash
wiverno docs --port 8001
```

Opens documentation at `http://127.0.0.1:8001`

**Note:** To build or deploy documentation, use the Makefile:

```bash
make docs        # Build static documentation
make docs-deploy # Deploy to GitHub Pages
```

## Help Command

Show comprehensive help and usage examples:

```bash
wiverno help
```

Displays:

- Available commands
- Command descriptions
- Usage examples
- Quick reference

## Environment Variables

Configure Wiverno behavior with environment variables:

```bash
# Development server
export WIVERNO_HOST=0.0.0.0
export WIVERNO_PORT=5000
export WIVERNO_DEBUG=true

# Documentation
export WIVERNO_DOCS_PORT=8001
```

## Configuration Files

### pyproject.toml

Project configuration:

```toml
[project]
name = "myapp"
version = "0.1.0"

[project.scripts]
myapp = "myapp.cli:main"
```

### mkdocs.yml

Documentation configuration (required for `wiverno docs`):

```yaml
site_name: My Application
theme:
  name: material

nav:
  - Home: index.md
  - Guide: guide.md
```

## Common Workflows

### Local Development

```bash
# Start development server
wiverno run dev

# In another terminal, serve docs
wiverno docs --port 8001
```

### Building for Production

```bash
# Test production mode locally
wiverno run prod

# Build documentation (use Makefile)
make docs

# Deploy everything
make docs-deploy
```

### CI/CD Pipeline

```bash
# Install dependencies
uv pip install -e .[dev]

# Run tests
pytest

# Build docs (use Makefile)
make docs

# Deploy (on main branch)
make docs-deploy
```

## Troubleshooting

### Module Not Found

```text
ERROR: Module 'run.py' not found in current directory.
```

**Solution:** Make sure you're in the project root or specify the correct module:

```bash
wiverno run dev --app-module myapp
```

### Application Not Found

```text
ERROR: Application 'app' not found in module 'run'
```

**Solution:** Check that your module has the correct variable name:

```python
# run.py
from wiverno.main import Wiverno

app = Wiverno()  # Must match --app-name
```

Or specify the correct name:

```bash
wiverno run dev --app-name application
```

### Port Already in Use

```text
ERROR: Address already in use
```

**Solution:** Use a different port:

```bash
wiverno run dev --port 3000
```

### MkDocs Not Installed

```text
ERROR: MkDocs is not installed.
```

**Solution:** Install documentation dependencies:

```bash
uv pip install mkdocs-material mkdocstrings[python]
```

Or install all dev dependencies:

```bash
uv pip install -e .[dev]
```

### mkdocs.yml Not Found

```text
ERROR: mkdocs.yml not found in current directory.
```

**Solution:** Create `mkdocs.yml` in your project root:

```yaml
site_name: My Project
theme:
  name: material
nav:
  - Home: index.md
```

## Advanced Usage

### Custom Module Structure

```bash
# For this structure:
# myproject/
#   myapp/
#     __init__.py
#     application.py  # contains 'wsgi_app'

wiverno run dev --app-module myapp.application --app-name wsgi_app
```

### Multiple Applications

```bash
# Development app
wiverno run dev --port 8000 --app-name dev_app

# Admin app (in another terminal)
wiverno run dev --port 8001 --app-name admin_app
```

### Docker Integration

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY . .
RUN pip install .

CMD ["wiverno", "run", "prod", "--host", "0.0.0.0", "--port", "8000"]
```

## Shell Completion

Enable shell completion (future feature):

```bash
# Bash
wiverno --install-completion bash

# Zsh
wiverno --install-completion zsh

# PowerShell
wiverno --install-completion powershell
```

## See Also

- [Development Setup](../dev/setup.md) - Set up development environment
- [Testing](../dev/testing.md) - Running tests
- [Workflow](../dev/workflow.md) - Development workflow
