# Server

The `RunServer` class provides a simple WSGI server implementation for running Wiverno applications. It uses Python's built-in `wsgiref.simple_server` for request handling.

## Module: `wiverno.core.server`

## Overview

`RunServer` is a lightweight WSGI server wrapper that's suitable for development and testing. For production deployments, use external WSGI servers like Gunicorn, uWSGI, or Waitress.

## Constructor

### `RunServer(application, host="localhost", port=8000)`

Creates a new server instance.

**Parameters:**

- `application` (Callable): A WSGI-compatible application
- `host` (str, optional): Hostname to bind to. Defaults to `"localhost"`
- `port` (int, optional): Port number to bind to. Defaults to `8000`

**Returns:** `RunServer` instance

```python
from wiverno.core.server import RunServer
from wiverno.main import Wiverno

app = Wiverno()

@app.get("/")
def home(request):
    return "200 OK", "Hello"

# Create server
server = RunServer(app, host="localhost", port=8000)
```

## Attributes

### `host: str`

The hostname the server is bound to.

```python
server = RunServer(app, host="0.0.0.0")
print(server.host)  # Output: 0.0.0.0
```

### `port: int`

The port number the server is bound to.

```python
server = RunServer(app, port=8000)
print(server.port)  # Output: 8000
```

### `application: Callable`

The WSGI application being served.

```python
server = RunServer(app)
print(server.application)  # Output: <Wiverno application>
```

## Methods

### `start() -> None`

Starts the WSGI server and serves the application forever.

The server will run indefinitely until interrupted by `KeyboardInterrupt` (Ctrl+C). This method blocks and doesn't return unless the server is stopped.

**Raises:**

- `KeyboardInterrupt` when user presses Ctrl+C (gracefully handled)

```python
server = RunServer(app, host="0.0.0.0", port=8000)
server.start()  # Blocks until Ctrl+C is pressed
```

## Usage Examples

### Basic Usage

```python
from wiverno.main import Wiverno
from wiverno.core.server import RunServer

app = Wiverno()

@app.get("/")
def home(request):
    return "200 OK", "<html><body>Hello!</body></html>"

if __name__ == "__main__":
    server = RunServer(app, host="localhost", port=8000)
    server.start()
```

Run with:
```bash
python app.py
# Server running at http://localhost:8000
```

### Custom Host and Port

```python
from wiverno.core.server import RunServer

# Listen on all network interfaces
server = RunServer(app, host="0.0.0.0", port=5000)
server.start()

# Now accessible at http://0.0.0.0:5000
```

### Development Server Setup

```python
from wiverno.main import Wiverno
from wiverno.core.server import RunServer

app = Wiverno()

@app.get("/")
def home(request):
    return "200 OK", "Home"

@app.get("/about")
def about(request):
    return "200 OK", "About"

if __name__ == "__main__":
    print("Starting development server...")
    print("Server running at http://localhost:8000")
    print("Press Ctrl+C to stop")

    server = RunServer(app)
    server.start()
```

## CLI Alternative

The Wiverno CLI provides a convenient way to start the server:

```bash
wiverno run dev app:app --host 0.0.0.0 --port 5000
```

This automatically creates a `RunServer` and starts it.

## Production Deployment

For production use, employ external WSGI servers instead of `RunServer`:

### Gunicorn

```bash
gunicorn app:app
```

### uWSGI

```bash
uwsgi --http :8000 --wsgi-file app.py --callable app
```

### Waitress

```python
from waitress import serve
from wiverno.main import Wiverno

app = Wiverno()

# ... define routes ...

if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=8000)
```

## Notes

- `RunServer` is intended for development and testing only
- Use external WSGI servers (Gunicorn, uWSGI, Waitress) for production
- The server binds to the specified host and port
- On Windows, use `"127.0.0.1"` instead of `"localhost"` if you encounter connection issues
- When binding to `"0.0.0.0"`, the server listens on all available network interfaces

## See Also

- [Application](application.md) - Wiverno application class
- [CLI](../cli.md) - Command-line interface
- [Workflow](../../dev/workflow.md) - Development workflow
