# DevServer

The `DevServer` class provides a development server with hot reload functionality. It automatically restarts your application when Python source files are modified, making development faster and more convenient.

## Module: `wiverno.dev.dev_server`

## Overview

`DevServer` is specifically designed for development environments and includes:

- **Hot Reload** - Automatically restarts when `.py` files change
- **Debouncing** - Prevents excessive restarts by grouping changes
- **File Watching** - Uses watchdog to monitor specified directories
- **Rich UI** - Beautiful console output with progress indicators
- **Configurable Ignoring** - Exclude specific files/directories from watching

**⚠️ Important:** DevServer is for development only. Do not use in production!

## Constructor

### `DevServer(app_module, app_name="app", host="localhost", port=8000, watch_dirs=None, ignore_patterns=None, debounce_seconds=1.0)`

Creates a new development server instance.

**Parameters:**

- `app_module` (str): Module path containing the WSGI application (e.g., `'run'`, `'myapp.main'`)
- `app_name` (str, optional): Name of the application variable in the module. Defaults to `"app"`
- `host` (str, optional): Server host address. Defaults to `"localhost"`
- `port` (int, optional): Server port. Defaults to `8000`
- `watch_dirs` (list[str], optional): Directories to watch for changes. If None, watches current directory
- `ignore_patterns` (list[str], optional): Patterns to ignore. Defaults to common patterns (see below)
- `debounce_seconds` (float, optional): Time to wait before restarting after file changes. Defaults to `1.0`

**Default Ignore Patterns:**

- `__pycache__/`
- `.venv/`, `venv/`
- `.git/`
- `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`
- `tests/`
- `htmlcov/`, `.coverage`

```python
from wiverno.dev.dev_server import DevServer

# Basic usage
server = DevServer(
    app_module="myapp",
    app_name="app",
    host="localhost",
    port=8000,
)
```

## Attributes

### `app_module: str`

Module path containing the WSGI application.

```python
server = DevServer(app_module="myapp.main")
print(server.app_module)  # Output: myapp.main
```

### `app_name: str`

Name of the application variable.

```python
server = DevServer(app_module="run", app_name="application")
print(server.app_name)  # Output: application
```

### `host: str`

Server host address.

```python
server = DevServer(app_module="run", host="0.0.0.0")
print(server.host)  # Output: 0.0.0.0
```

### `port: int`

Server port number.

```python
server = DevServer(app_module="run", port=8080)
print(server.port)  # Output: 8080
```

### `watch_dirs: list[str]`

List of directories to watch for changes.

```python
server = DevServer(
    app_module="run",
    watch_dirs=["./myapp", "./shared"],
)
print(server.watch_dirs)  # Output: ['./myapp', './shared']
```

### `ignore_patterns: list[str]`

List of patterns to ignore when watching for changes.

```python
server = DevServer(
    app_module="run",
    ignore_patterns=["__pycache__", "*.pyc", ".venv"],
)
print(server.ignore_patterns)
```

### `debounce_seconds: float`

Time to wait before restarting after file changes.

```python
server = DevServer(app_module="run", debounce_seconds=2.0)
print(server.debounce_seconds)  # Output: 2.0
```

## Methods

### `serve(app_module="run", app_name="app", host="localhost", port=8000)` [static]

Main entry point for running the development server. This is the recommended way to start the server.

**Parameters:**

- `app_module` (str, optional): Module path containing the WSGI application. Defaults to `"run"`
- `app_name` (str, optional): Name of the application variable. Defaults to `"app"`
- `host` (str, optional): Server host address. Defaults to `"localhost"`
- `port` (int, optional): Server port. Defaults to `8000`

**Returns:** None (blocks until interrupted)

```python
from wiverno.dev.dev_server import DevServer

# Quick start
DevServer.serve()

# Custom configuration
DevServer.serve(
    app_module="myapp",
    app_name="application",
    host="0.0.0.0",
    port=8080,
)
```

### `stop() -> None`

Stop the development server and file watcher.

Gracefully shuts down the server process and stops file watching.

```python
server = DevServer(app_module="run")

# In another thread or signal handler
server.stop()
```

## Usage Examples

### Quick Start

```python
from wiverno.dev.dev_server import DevServer

# Simplest form - uses defaults (run.py with 'app' variable)
DevServer.serve()
```

### Custom Configuration

```python
DevServer.serve(
    app_module="myproject.api",
    app_name="application",
    host="0.0.0.0",
    port=5000,
)
```

For more detailed examples and project structure, see the [Running Guide](../../guide/running.md).

### Advanced Configuration

```python
from wiverno.dev.dev_server import DevServer

server = DevServer(
    app_module="myapp",
    app_name="app",
    host="0.0.0.0",
    port=8000,
    watch_dirs=[
        "./myapp",          # Watch application code
        "./shared",         # Watch shared utilities
        "./config",         # Watch configuration
    ],
    ignore_patterns=[
        "__pycache__",
        "*.pyc",
        ".venv",
        "venv",
        "tests",
        "*.log",
        ".git",
    ],
    debounce_seconds=1.5,  # Wait 1.5 seconds before restart
)

# Use serve() static method for actual startup
# DevServer.serve(...)
```

### Project Structure Example

```
myproject/
├── myapp/
│   ├── __init__.py
│   ├── main.py       # Contains 'app'
│   └── routes.py
├── dev.py            # Development server script
└── run.py            # Production server script
```

`dev.py`:

```python
from wiverno.dev.dev_server import DevServer

if __name__ == "__main__":
    DevServer.serve(
        app_module="myapp.main",
        app_name="app",
        host="127.0.0.1",
        port=8000,
    )
```

Run with:

```bash
uv run python dev.py
```

### Hot Reload in Action

When you save a file:

```
WARNING: File changed: /path/to/myapp/routes.py
>> Server restarting...
╭────────────────────────────────────────╮
│ Wiverno Development Server             │
│                                        │
│ Server: http://localhost:8000          │
│ Debug Mode: ON                         │
│ Restart: #2                            │
│ Press Ctrl+C to stop                   │
╰────────────────────────────────────────╯
```

## How Hot Reload Works

DevServer uses the watchdog library to monitor file changes:

1. Monitors `.py` files in specified directories
2. Debounces changes (waits `debounce_seconds` before restart)
3. Terminates old process gracefully
4. Spawns new process with updated code

See the [Running Guide](../../guide/running.md#how-hot-reload-works) for detailed explanation.

## CLI Alternative

Use the Wiverno CLI for quick development server starts:

```bash
# Start dev server with defaults
wiverno run dev

# Custom configuration
wiverno run dev --host 0.0.0.0 --port 8080

# Specify module and app
wiverno run dev --app-module myapp --app-name application
```

## Best Practices

### Use for Development Only

```python
# ✅ Good - Development
if __name__ == "__main__":
    from wiverno.dev.dev_server import DevServer
    DevServer.serve()

# ❌ Bad - Don't use in production
if __name__ == "__main__":
    from wiverno.dev.dev_server import DevServer
    DevServer.serve(host="0.0.0.0")  # Exposed to internet!
```

### Configure Ignore Patterns

Ignore files that shouldn't trigger restarts:

```python
DevServer.serve(
    app_module="myapp",
    ignore_patterns=[
        "__pycache__",
        "*.pyc",
        ".venv",
        "tests",           # Don't restart on test changes
        "*.log",           # Ignore log files
        "static/",         # Ignore static assets
        "migrations/",     # Ignore database migrations
    ],
)
```

### Separate Dev and Production Scripts

```python
# dev.py - Development only
from wiverno.dev.dev_server import DevServer

if __name__ == "__main__":
    DevServer.serve(app_module="myapp")

# run.py - Production
from wiverno.core.server import RunServer
from myapp import app

if __name__ == "__main__":
    server = RunServer(app, host="0.0.0.0", port=8000)
    server.start()
```

### Adjust Debounce Time

For different workflows:

```python
# Fast restarts (may restart too often)
DevServer.serve(debounce_seconds=0.5)

# Slower restarts (better for large projects)
DevServer.serve(debounce_seconds=2.0)

# Default (recommended)
DevServer.serve(debounce_seconds=1.0)
```

## Troubleshooting

### Hot Reload Not Working

**Problem:** Files change but server doesn't restart.

**Solutions:**

1. Check file is not in ignore patterns
2. Verify file has `.py` extension
3. Ensure file is in watched directories
4. Check console for error messages

```python
# Debug: Print watch directories
server = DevServer(
    app_module="myapp",
    watch_dirs=["./myapp"],  # Explicit watch directory
)
print(f"Watching: {server.watch_dirs}")
```

### Too Many Restarts

**Problem:** Server restarts constantly.

**Solutions:**

1. Increase debounce time
2. Add patterns to ignore list
3. Check for auto-save or backup files

```python
DevServer.serve(
    debounce_seconds=2.0,  # Wait longer
    ignore_patterns=[
        "__pycache__",
        "*.swp",         # Vim swap files
        "*.tmp",         # Temp files
        "*~",            # Backup files
    ],
)
```

### Import Errors

**Problem:** `ImportError: No module named 'myapp'`

**Solutions:**

1. Verify module path is correct
2. Check PYTHONPATH
3. Ensure `__init__.py` exists in package directories

```python
# Wrong
DevServer.serve(app_module="myapp")  # Looking for myapp.py

# Correct
DevServer.serve(app_module="myapp.main")  # Looking for myapp/main.py
```

### Port Already in Use

**Problem:** `OSError: Address already in use`

**Solutions:**

```bash
# Find and kill process
lsof -i :8000
kill -9 <PID>

# Or use different port
DevServer.serve(port=8001)
```

## Related Documentation

- [Running Your Application](../../guide/running.md) - Complete guide on development and production servers
- [RunServer](../core/server.md) - Production server documentation
- [CLI Commands](../cli.md) - Command-line interface

## Comparison with RunServer

| Feature               | DevServer         | RunServer             |
| --------------------- | ----------------- | --------------------- |
| **Hot Reload**        | ✅ Yes            | ❌ No                 |
| **Purpose**           | Development       | Production            |
| **Performance**       | Lower             | Higher                |
| **File Watching**     | ✅ Yes            | ❌ No                 |
| **Graceful Shutdown** | ✅ Yes            | ✅ Yes                |
| **Dependencies**      | watchdog, rich    | None                  |
| **Use Case**          | Local development | Production deployment |

## Summary

- Use `DevServer` for all development work
- It automatically restarts when code changes
- Configure ignore patterns to avoid unnecessary restarts
- **Never use in production** - use RunServer or Gunicorn instead
- Main entry point is `DevServer.serve()` static method
