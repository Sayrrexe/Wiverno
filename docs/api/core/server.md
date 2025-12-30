# Server

The `RunServer` class provides a production-ready WSGI server implementation for running Wiverno applications. It uses Python's built-in `wsgiref.simple_server` with enhanced features for stability and production use.

## Module: `wiverno.core.server`

## Overview

`RunServer` is an improved WSGI server that includes:

- **Graceful shutdown** - Handles SIGINT and SIGTERM signals properly
- **Enhanced logging** - Detailed startup and error information
- **Error handling** - Better exception handling and recovery
- **Configurable queue size** - Tune for your workload

While suitable for light to medium traffic production environments, for high-traffic applications consider using dedicated WSGI servers like Gunicorn, uWSGI, or Waitress.

## Constructor

### `RunServer(application, host="localhost", port=8000, request_queue_size=5)`

Creates a new server instance.

**Parameters:**

- `application` (Callable): A WSGI-compatible application
- `host` (str, optional): Hostname to bind to. Defaults to `"localhost"`
- `port` (int, optional): Port number to bind to. Defaults to `8000`
- `request_queue_size` (int, optional): Maximum number of queued connections. Defaults to `5`

**Returns:** `RunServer` instance

```python
from wiverno.core.server import RunServer
from wiverno.main import Wiverno

app = Wiverno()

@app.get("/")
def home(request):
    return "200 OK", "Hello"

# Create server with custom queue size
server = RunServer(app, host="localhost", port=8000, request_queue_size=10)
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

### `request_queue_size: int`

Maximum number of queued connections.

```python
server = RunServer(app, request_queue_size=10)
print(server.request_queue_size)  # Output: 10
```

## Methods

### `start() -> None`

Starts the WSGI server and serves the application forever.

The server will run indefinitely until interrupted by `KeyboardInterrupt` (Ctrl+C) or SIGTERM signal. This method blocks and doesn't return unless the server is stopped.

Features:

- Handles SIGINT (Ctrl+C) and SIGTERM signals gracefully
- Completes current requests before shutting down
- Logs startup information and errors
- Automatically cleans up resources

**Raises:**

- `OSError`: If unable to bind to the specified host:port
- `Exception`: For unexpected errors during server operation

```python
import logging

logging.basicConfig(level=logging.INFO)

server = RunServer(app, host="0.0.0.0", port=8000)
server.start()  # Blocks until interrupted

# Logs:
# INFO: Wiverno server started on http://0.0.0.0:8000
# INFO: Request queue size: 5
# INFO: Press Ctrl+C to stop the server
```

### `stop() -> None`

Stops the server gracefully.

Shuts down the server, allowing current requests to complete before stopping. This method is called automatically on SIGINT/SIGTERM or can be called programmatically.

```python
server = RunServer(app)

# In another thread or signal handler:
server.stop()  # Graceful shutdown
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
python run.py
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

### Production Setup with Logging

```python
import logging
from wiverno.main import Wiverno
from wiverno.core.server import RunServer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

app = Wiverno()

@app.get("/")
def home(request):
    return "200 OK", "Home"

@app.get("/api/health")
def health(request):
    return "200 OK", '{"status": "ok"}'

if __name__ == "__main__":
    server = RunServer(
        app,
        host="0.0.0.0",
        port=8000,
        request_queue_size=10,  # Handle more concurrent connections
    )

    try:
        server.start()
    except OSError as e:
        logging.error(f"Failed to start server: {e}")
    except KeyboardInterrupt:
        logging.info("Server stopped by user")
```

### Error Handling

```python
from wiverno.core.server import RunServer

try:
    # Try to bind to privileged port
    server = RunServer(app, host="0.0.0.0", port=80)
    server.start()
except OSError as e:
    if "Permission denied" in str(e):
        print("Error: Port 80 requires root privileges")
        print("Try: sudo python run.py")
        print("Or use port >= 1024")
    elif "Address already in use" in str(e):
        print("Error: Port 80 is already in use")
        print("Kill the process or use a different port")
```

### Programmatic Stop

```python
import threading
import time
from wiverno.core.server import RunServer

server = RunServer(app, host="localhost", port=8000)

# Start server in a thread
server_thread = threading.Thread(target=server.start, daemon=True)
server_thread.start()

# Do some work...
time.sleep(60)

# Stop server gracefully
server.stop()
```

## Comparison with Other Servers

### RunServer (Built-in)

**Pros:**

- No additional dependencies
- Graceful shutdown
- Good for light to medium traffic

- Easy to configure

**Cons:**

- Single-threaded
- Not optimized for high traffic
- Limited performance tuning

**Best for:** Small to medium applications, prototypes, internal tools

### Gunicorn (Recommended for Production)

```bash
pip install gunicorn

gunicorn myapp:app --workers 4 --bind 0.0.0.0:8000
```

**Pros:**

- Multi-worker support

- High performance
- Production-proven
- Many configuration options

**Cons:**

- Unix/Linux only
- Additional dependency

### Waitress (Cross-platform)

```bash
pip install waitress
waitress-serve --host=0.0.0.0 --port=8000 myapp:app
```

**Pros:**

- Cross-platform (Windows support)
- Multi-threaded
- Production-ready

**Cons:**

- Additional dependency
- Fewer features than Gunicorn

## Best Practices

### Development

Use DevServer for development with hot reload:

```python
from wiverno.dev.dev_server import DevServer

DevServer.serve(app_module="myapp", port=8000)
```

See [Running Your Application](../../guide/running.md) for details.

### Production

For production, choose based on traffic:

**Light Traffic** (< 100 req/sec):

```python
# Use RunServer
server = RunServer(app, host="0.0.0.0", port=8000, request_queue_size=10)
server.start()

```

**Medium to High Traffic**:

```bash
# Use Gunicorn
gunicorn myapp:app --workers 4 --worker-class sync --bind 0.0.0.0:8000
```

**Very High Traffic**:

```bash
# Use Gunicorn with multiple workers + nginx reverse proxy
gunicorn myapp:app \
    --workers 8 \
    --worker-class sync \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --bind 127.0.0.1:8000
```

## Troubleshooting

### Port Already in Use

```bash
# Find process using the port
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use a different port
server = RunServer(app, port=8001)
```

### Permission Denied (Port < 1024)

```bash
# Option 1: Use sudo (not recommended)
sudo python run.py

# Option 2: Use port >= 1024 (recommended)
server = RunServer(app, port=8000)

# Option 3: Use authbind (Linux)
authbind --deep python run.py
```

### Server Not Accessible from External Network

```python
# Wrong: Only accessible from localhost
server = RunServer(app, host="localhost", port=8000)

# Correct: Accessible from external network
server = RunServer(app, host="0.0.0.0", port=8000)
```

## Related Documentation

- [Running Your Application](../../guide/running.md) - Comprehensive guide on development and production servers
- [CLI Commands](../cli.md) - Command-line interface for server management
- [Application](application.md) - Wiverno application class

## CLI Alternative

The Wiverno CLI provides a convenient way to start the server:

```bash
# Run production server
wiverno run prod --host 0.0.0.0 --port 8000

# Run development server with hot reload
wiverno run dev --host 0.0.0.0 --port 8000
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
