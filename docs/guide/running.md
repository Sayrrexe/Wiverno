# Running Your Application

This guide explains how to run your Wiverno application in different environments, from development to production.

## Overview

Wiverno provides two server options:

- **DevServer** - Development server with hot reload (automatic restart on code changes)
- **RunServer** - Production-ready WSGI server for deploying applications

## Development Server (DevServer)

The `DevServer` is designed for local development and includes hot reload functionality. When you modify your Python files, the server automatically restarts to reflect the changes.

### Basic Usage

```python
from wiverno.dev.dev_server import DevServer

# Quick start with defaults
DevServer.serve()
```

This starts the server with default settings:

- **Module**: `run` (looks for `run.py`)
- **App name**: `app` (looks for `app` variable)
- **Host**: `localhost`
- **Port**: `8000`

### Custom Configuration

```python
DevServer.serve(
    app_module="myapp",      # Module containing your app
    app_name="application",  # Variable name of your app
    host="0.0.0.0",         # Bind to all interfaces
    port=8080               # Custom port
)
```

### Advanced Usage

For more control, create a DevServer instance:

```python
from wiverno.dev.dev_server import DevServer

server = DevServer(
    app_module="myapp",
    app_name="app",
    host="localhost",
    port=8000,
    watch_dirs=["./myapp", "./shared"],  # Watch multiple directories
    ignore_patterns=[                     # Custom ignore patterns
        "__pycache__",
        ".venv",
        "tests",
        "*.pyc",
    ],
    debounce_seconds=1.0,  # Wait time before restart
)

# For advanced usage, instantiate and configure before serving
# Then use serve() static method for actual startup
```

### How Hot Reload Works

1. **Watchdog** monitors `.py` files in specified directories
2. When a file is modified, a `FileSystemEvent` is triggered
3. **Debounce mechanism** waits 1 second to collect all changes
4. After the delay, server restart is initiated
5. Old server process is properly terminated
6. New process starts with updated code
7. Restart counter increments for tracking

### Ignored Patterns

By default, DevServer ignores:

- `__pycache__/` - Python cache directories
- `.venv/`, `venv/` - Virtual environments
- `.git/` - Git repository
- `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/` - Tool caches
- `tests/` - Test directories
- `htmlcov/`, `.coverage` - Coverage files

### Example Development Setup

Create a `dev.py` file in your project:

```python
from wiverno.dev.dev_server import DevServer

if __name__ == "__main__":
    DevServer.serve(
        app_module="app",
        app_name="app",
        host="0.0.0.0",
        port=8000,
    )
```

Run it:

```bash
uv run python dev.py
```

### Using with CLI

The CLI provides a convenient way to run the dev server:

```bash
# Start development server
wiverno run dev

# With custom host and port
wiverno run dev --host 0.0.0.0 --port 8000

# With custom module
wiverno run dev --app-module myapp --app-name application
```

## Production Server (RunServer)

The `RunServer` is an improved WSGI server suitable for production deployments. It includes graceful shutdown, better error handling, and production-ready features.

### Basic Usage

```python
from wiverno.core.server import RunServer
from myapp import app

server = RunServer(app, host="0.0.0.0", port=8000)
server.start()
```

### Configuration Options

```python
server = RunServer(
    application=app,           # Your WSGI application
    host="0.0.0.0",           # Bind to all interfaces
    port=8000,                # Port number
    request_queue_size=5,     # Max queued connections
)
```

### Features

#### Graceful Shutdown

RunServer handles SIGINT (Ctrl+C) and SIGTERM signals gracefully:

```python
server = RunServer(app)
server.start()  # Server runs until interrupted

# On Ctrl+C or kill signal:
# 1. Current requests are completed
# 2. Server shuts down cleanly
# 3. Resources are released
```

You can also stop the server programmatically:

```python
server.stop()  # Graceful shutdown
```

#### Enhanced Logging

RunServer provides detailed logging:

```python
import logging

logging.basicConfig(level=logging.INFO)

server = RunServer(app, host="0.0.0.0", port=8000)
server.start()

# Logs:
# INFO: Wiverno server started on http://0.0.0.0:8000
# INFO: Request queue size: 5
# INFO: Press Ctrl+C to stop the server
```

#### Error Handling

The server handles common errors:

```python
try:
    server = RunServer(app, host="0.0.0.0", port=80)
    server.start()
except OSError as e:
    print(f"Cannot bind to port 80: {e}")
    # Permission denied or port already in use
```

### Example Production Setup

Create a `run.py` file:

```python
import logging
from wiverno.core.server import RunServer
from myapp import app

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

if __name__ == "__main__":
    server = RunServer(
        app,
        host="0.0.0.0",
        port=8000,
        request_queue_size=10,  # Handle more concurrent connections
    )

    try:
        server.start()
    except KeyboardInterrupt:
        print("Server stopped")
```

Run it:

```bash
uv run python run.py
```

### Using with CLI

```bash
# Start production server
wiverno run prod

# With custom configuration
wiverno run prod --host 0.0.0.0 --port 8000
```

## Production Deployment Recommendations

### For Light to Medium Traffic

RunServer is suitable for light to medium traffic applications:

```python
server = RunServer(
    app,
    host="0.0.0.0",
    port=8000,
    request_queue_size=10,
)
server.start()
```

**Pros**:

- Built-in, no extra dependencies
- Graceful shutdown
- Easy to configure
- Good error handling

**Cons**:

- Single-threaded (no concurrency)
- Not optimized for high traffic
- Limited performance tuning options

### For High Traffic (Recommended)

For production environments with high traffic, use dedicated WSGI servers:

#### Gunicorn (Linux/Unix)

```bash
pip install gunicorn
gunicorn myapp:app --workers 4 --bind 0.0.0.0:8000
```

#### Waitress (Cross-platform)

```bash
pip install waitress
waitress-serve --host=0.0.0.0 --port=8000 myapp:app
```

#### uWSGI (Linux/Unix)

```bash
pip install uwsgi
uwsgi --http :8000 --wsgi-file myapp.py --callable app --processes 4
```

## Comparison Table

| Feature               | DevServer      | RunServer        | Gunicorn/uWSGI   |
| --------------------- | -------------- | ---------------- | ---------------- |
| **Purpose**           | Development    | Light production | Heavy production |
| **Hot Reload**        | ✅ Yes         | ❌ No            | ❌ No            |
| **Multi-process**     | ❌ No          | ❌ No            | ✅ Yes           |
| **Graceful Shutdown** | ✅ Yes         | ✅ Yes           | ✅ Yes           |
| **Performance**       | Low            | Medium           | High             |
| **Ease of Use**       | Very Easy      | Easy             | Moderate         |
| **Dependencies**      | watchdog, rich | None             | Extra package    |

## Best Practices

### Development

1. **Use DevServer** for all development work
2. **Don't use DevServer in production** - it's not designed for it
3. **Configure ignore patterns** to avoid unnecessary restarts
4. **Use appropriate debounce time** (1 second is usually good)

Example:

```python
# dev.py
from wiverno.dev.dev_server import DevServer

if __name__ == "__main__":
    DevServer.serve(
        app_module="myapp",
        host="127.0.0.1",  # Only localhost in dev
        port=8000,
    )
```

### Production

1. **Test with RunServer first** before moving to Gunicorn/uWSGI
2. **Use RunServer for small applications** or prototypes
3. **Use Gunicorn/uWSGI/Waitress for production** applications
4. **Enable proper logging** for debugging
5. **Use reverse proxy** (nginx, Apache) in front of your WSGI server
6. **Monitor resource usage** and adjust workers/threads accordingly

Example:

```python
# run.py
import logging
from wiverno.core.server import RunServer
from myapp import app

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
)

if __name__ == "__main__":
    server = RunServer(app, host="0.0.0.0", port=8000)
    server.start()
```

### Systemd Service (Linux)

Create `/etc/systemd/system/wiverno-app.service`:

```ini
[Unit]
Description=Wiverno Application
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/myapp
Environment="PATH=/var/www/myapp/.venv/bin"
ExecStart=/var/www/myapp/.venv/bin/python run.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable wiverno-app
sudo systemctl start wiverno-app
sudo systemctl status wiverno-app
```

## Docker Deployment

### Dockerfile Example

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run with RunServer (for simple apps)
CMD ["python", "run.py"]

# Or use Gunicorn for production
# CMD ["gunicorn", "myapp:app", "--workers=4", "--bind=0.0.0.0:8000"]
```

### Docker Compose Example

```yaml
version: "3.8"

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - PYTHONUNBUFFERED=1
    volumes:
      - .:/app # For development with hot reload
    # Remove volumes in production
```

## Troubleshooting

### Port Already in Use

```python
# Error: OSError: [Errno 98] Address already in use

# Solution: Use a different port or kill the process using the port
# Find process:
# lsof -i :8000
# Kill process:
# kill -9 <PID>
```

### Hot Reload Not Working

1. Check that you're using DevServer, not RunServer
2. Verify file patterns are not in ignore list
3. Make sure files are being saved properly
4. Check console for error messages

### Permission Denied on Port 80/443

```bash
# Ports below 1024 require root privileges
# Option 1: Use port >= 1024 (recommended)
DevServer.serve(port=8000)

# Option 2: Use sudo (not recommended)
sudo python dev.py

# Option 3: Use reverse proxy (best for production)
# nginx -> localhost:8000
```

### High Memory Usage in Production

RunServer is single-threaded, but if you see high memory usage:

1. Check for memory leaks in your application code
2. Monitor with tools like `htop` or `ps`
3. Consider using Gunicorn with multiple workers:

```bash
gunicorn myapp:app --workers 4 --max-requests 1000 --max-requests-jitter 100
```

## Summary

- **DevServer**: Development with hot reload - use `DevServer.serve()`
- **RunServer**: Light production - use for small apps or prototypes
- **Gunicorn/uWSGI/Waitress**: Heavy production - use for production applications
- Always use proper logging and monitoring in production
- Test thoroughly before deploying to production

## Next Steps

- Learn about [CLI commands](cli.md) for quick server management
- Explore [Routing](routing.md) to define your application endpoints
- Read about [Requests](requests.md) to handle incoming data
