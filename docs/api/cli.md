# CLI Reference

The Wiverno CLI provides command-line tools for running and managing Wiverno applications.

## Module: `wiverno.cli`

## Overview

The CLI is built with [Typer](https://typer.tiangolo.com/) and provides commands for:

- Running development servers with hot reload
- Running production servers
- Serving documentation
- Getting help and usage information

## Installation

The CLI is automatically installed when you install Wiverno:

```bash
pip install wiverno
```

## Global Options

All commands support `--help` to show detailed help:

```bash
wiverno --help
wiverno run --help
wiverno run dev --help
```

## Commands

### `wiverno run dev`

Start a development server with automatic hot reload.

**Usage:**

```bash
wiverno run dev [OPTIONS]
```

**Options:**

- `--host, -h TEXT` - Server host address
  - Default: `localhost`
  - Example: `--host 0.0.0.0` to listen on all interfaces

- `--port, -p INTEGER` - Server port number
  - Default: `8000`
  - Example: `--port 3000` to use port 3000

- `--app-module, -m TEXT` - Module containing the WSGI application
  - Default: `run`
  - Example: `--app-module app` to load from `app.py`
  - Example: `--app-module myapp.wsgi` to load from `myapp/wsgi.py`

- `--app-name, -a TEXT` - Name of the application variable in the module
  - Default: `app`
  - Example: `--app-name application` to use variable `application`

- `--watch, -w TEXT` - Comma-separated list of directories to watch
  - Default: Current directory
  - Example: `--watch src,templates` to watch specific directories

**Examples:**

```bash
# Start development server with defaults
wiverno run dev

# Use custom port
wiverno run dev --port 3000

# Listen on all network interfaces
wiverno run dev --host 0.0.0.0

# Custom app location
wiverno run dev --app-module myapp --app-name application

# Watch specific directories
wiverno run dev --watch src,templates
```

**Features:**

- Automatic restart on file changes (Python, HTML, CSS, JS)
- Live reload enabled
- Detailed error messages with tracebacks
- Graceful shutdown with Ctrl+C

### `wiverno run prod`

Start a production server without automatic restarts.

**Usage:**

```bash
wiverno run prod [OPTIONS]
```

**Options:**

- `--host, -h TEXT` - Server host address
  - Default: `localhost`
  - Example: `--host 0.0.0.0`

- `--port, -p INTEGER` - Server port number
  - Default: `8000`
  - Example: `--port 8080`

- `--app-module, -m TEXT` - Module containing the WSGI application
  - Default: `run`

- `--app-name, -a TEXT` - Name of the application variable in the module
  - Default: `app`

**Examples:**

```bash
# Start production server with defaults
wiverno run prod

# Use custom host and port
wiverno run prod --host 0.0.0.0 --port 8080

# Custom app location
wiverno run prod --app-module myapp --app-name application
```

**Notes:**

- No automatic restarts on file changes
- No file watching
- Suitable for deployment environments
- For better production setup, use external WSGI servers (Gunicorn, uWSGI, Waitress)

### `wiverno docs`

Serve project documentation using MkDocs with live reload.

**Usage:**

```bash
wiverno docs [OPTIONS]
```

**Options:**

- `--host, -h TEXT` - Documentation server host
  - Default: `127.0.0.1`

- `--port, -p INTEGER` - Documentation server port
  - Default: `8000`

- `--open/--no-open` - Open browser automatically
  - Default: `--open`
  - Use `--no-open` to prevent automatic browser opening

**Examples:**

```bash
# Serve docs at default address
wiverno docs

# Use custom port
wiverno docs --port 8001

# Don't open browser automatically
wiverno docs --no-open

# Listen on all interfaces
wiverno docs --host 0.0.0.0
```

**Requirements:**

- `mkdocs.yml` file in project root
- MkDocs installed: `pip install mkdocs-material mkdocstrings[python]`

**Features:**

- Live reload on documentation changes
- Automatic browser opening
- Built on MkDocs with Material theme

### `wiverno start`

Quick start command (placeholder for future features).

**Usage:**

```bash
wiverno start
```

**Status:** Currently a placeholder. Future versions will include:
- Project scaffolding
- Template generation
- Configuration wizard

### `wiverno help`

Show comprehensive help with available commands and examples.

**Usage:**

```bash
wiverno help
```

Displays:
- Overview of Wiverno
- List of available commands
- Usage examples for common tasks
- Documentation links

## Common Workflows

### Basic Development Setup

1. Create your application file `app.py`:

```python
from wiverno.main import Wiverno

app = Wiverno()

@app.get("/")
def home(request):
    return "200 OK", "Hello, World!"
```

2. Start development server:

```bash
wiverno run dev
```

3. Visit http://localhost:8000

### Custom Project Structure

For a project with custom structure:

1. Application in `myapp/wsgi.py`:

```python
from wiverno.main import Wiverno

app = Wiverno()

@app.get("/")
def home(request):
    return "200 OK", "Hello"
```

2. Run with custom module path:

```bash
wiverno run dev --app-module myapp.wsgi
```

### Multiple Directories

To watch multiple directories for changes:

```bash
wiverno run dev --watch src,templates,static
```

### Production Deployment

For production, use external WSGI servers:

```bash
# Create production app file
cat > production.py << 'EOF'
from app import app
EOF

# Run with Gunicorn
gunicorn production:app --bind 0.0.0.0:8000
```

Or use the prod command for testing:

```bash
wiverno run prod --host 0.0.0.0 --port 8000
```

## Environment Variables

The CLI respects common environment variables:

```bash
# Set Python path
export PYTHONPATH=/path/to/project

# Run with custom Python path
wiverno run dev
```

## Exit Codes

- `0` - Success
- `1` - Error (missing module, configuration error, etc.)

## Troubleshooting

### Module Not Found

**Error:** `ERROR: Module 'app.py' not found in current directory`

**Solution:**
- Make sure you're in the project root directory
- Check the module name with `-m` option
- Use `--app-module` to specify correct path

### Application Variable Not Found

**Error:** `ERROR: Application 'app' not found in module 'run'`

**Solution:**
- Ensure your module has the application variable
- Use `--app-name` to specify the correct variable name
- Example: `wiverno run dev --app-name application`

### MkDocs Not Installed

**Error:** `ERROR: MkDocs is not installed`

**Solution:**
```bash
pip install mkdocs-material mkdocstrings[python]
```

Or install all dev dependencies:
```bash
uv pip install -e .[dev]
```

### Port Already in Use

**Error:** `Address already in use`

**Solution:**
- Use a different port: `wiverno run dev --port 3000`
- Kill process using the port
- Wait and retry

## See Also

- [Application](core/application.md) - Wiverno application class
- [Server](core/server.md) - RunServer class
- [Workflow](../dev/workflow.md) - Development workflow
