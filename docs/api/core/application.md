# Application

The `Wiverno` class is the main entry point for creating web applications with Wiverno.

## Module: `wiverno.main`

::: wiverno.main.Wiverno
options:
show_root_heading: true
show_source: true
heading_level: 2

## Overview

The `Wiverno` class initializes your application with routes and handles the WSGI interface. It's responsible for:

- Route registration and management
- Request routing to appropriate handlers
- Response generation
- Error handling

## Basic Usage

```python
from wiverno.main import Wiverno

app = Wiverno()

@app.get("/")
def index(request):
    return "200 OK", "Hello, World!"
```

Or with route list (alternative approach):

```python
from wiverno.main import Wiverno

def index(request):
    return "200 OK", "Hello, World!"

app = Wiverno(routes_list=[
    ("/", index),
])
```

## Constructor Parameters

### routes_list

**Type:** `list[tuple[str, Callable | type]] | None`
**Default:** `None`

A list of tuples containing URL paths and their handlers. Each tuple consists of:

- **Pattern** (str): URL path (no dynamic parameters supported)
- **Handler** (Callable | type): Function or class-based view

**Examples:**

```python
# Function-based views
routes = [
    ("/", index_view),
    ("/about", about_view),
    ("/users", users_view),
]

# Class-based views
from wiverno.views.base_views import BaseView

class UserView(BaseView):
    def get(self, request):
        return "200 OK", "User list"

routes = [
    ("/users", UserView),
]

# Mixed
routes = [
    ("/", index_view),
    ("/api/users", UserView),
]
```

### debug_mode

**Type:** `bool`
**Default:** `True`

Enable or disable debug mode. In debug mode, exception tracebacks are passed to the 500 error handler for display.

```python
app = Wiverno(debug_mode=False)  # Production mode
```

### system_template_path

**Type:** `str`
**Default:** Built-in system templates path

Path to the directory containing system error templates (404, 405, 500). This is typically set to the internal `wiverno/static/templates` directory.

```python
app = Wiverno(system_template_path="/custom/error/templates")
```

### page_404

**Type:** `Callable[[Request], tuple[str, str]]`
**Default:** `PageNotFound404()`

Custom error handler for 404 Not Found errors. The handler receives a `Request` object and must return a tuple of `(status_string, html_body)`.

```python
def custom_404(request):
    return "404 NOT FOUND", "<html><body>Page not found</body></html>"

app = Wiverno(page_404=custom_404)
```

### page_405

**Type:** `Callable[[Request], tuple[str, str]]`
**Default:** `MethodNotAllowed405()`

Custom error handler for 405 Method Not Allowed errors. Receives a `Request` object.

```python
def custom_405(request):
    return "405 METHOD NOT ALLOWED", "<html><body>Method not allowed</body></html>"

app = Wiverno(page_405=custom_405)
```

### page_500

**Type:** `Callable[[Request, str | None], tuple[str, str]]`
**Default:** `InternalServerError500()`

Custom error handler for 500 Internal Server Error. Receives a `Request` object and an optional `error_traceback` string (only in debug mode).

```python
def custom_500(request, error_traceback=None):
    return "500 INTERNAL SERVER ERROR", "<html><body>Server error</body></html>"

app = Wiverno(page_500=custom_500)
```

## Routing Methods

The `Wiverno` class provides decorator methods for all HTTP methods:

### `@app.route(path, methods=None)`

Generic route decorator. Register a route with specific HTTP methods or all methods if `methods=None`.

```python
@app.route("/api/data", methods=["GET", "POST"])
def handle_data(request):
    return "200 OK", "Data"
```

### `@app.get(path)`, `@app.post(path)`, `@app.put(path)`, `@app.patch(path)`, `@app.delete(path)`

HTTP method-specific decorators. Available for GET, POST, PUT, PATCH, DELETE.

```python
@app.get("/users")
def list_users(request):
    return "200 OK", "Users list"

@app.post("/users")
def create_user(request):
    return "201 CREATED", "User created"
```

### `@app.connect(path)`, `@app.head(path)`, `@app.options(path)`, `@app.trace(path)`

Additional HTTP method decorators for CONNECT, HEAD, OPTIONS, and TRACE methods.

### `app.include_router(router, prefix="")`

Include routes from a `Router` instance with an optional URL prefix.

**Parameters:**

- `router` (Router): Router instance containing routes to include
- `prefix` (str, optional): URL prefix to prepend to all router paths

**Example:**

```python
from wiverno.core.router import Router

api_router = Router()

@api_router.get("/users")
def api_users(request):
    return "200 OK", "API Users"

app.include_router(api_router, prefix="/api")
# Routes become /api/users
```

## Methods

### `__call__(environ, start_response)`

The WSGI application callable. This method is called by the WSGI server for each request.

**Parameters:**

- `environ` (dict): WSGI environment dictionary
- `start_response` (Callable): WSGI start_response callable

**Returns:** Iterator of bytes representing the response body

**Note:** You typically don't call this method directly. It's used by the WSGI server.

## Attributes

### `debug`

**Type:** `bool`

Debug mode flag. Set to `True` to enable debug mode (tracebacks shown in 500 errors), `False` for production.

### `system_templator`

**Type:** `Templator`

The internal templator instance used to render system error templates (404, 405, 500).

### `page_404`, `page_405`, `page_500`

**Type:** `Callable`

The error handler callables for 404, 405, and 500 errors respectively.

## Examples

### Basic Application

```python
from wiverno.main import Wiverno

app = Wiverno()

@app.get("/")
def home(request):
    return "200 OK", "Welcome home!"

@app.get("/about")
def about(request):
    return "200 OK", "About us"
```

Run with:

```bash
wiverno run dev app:app
```

### With Templates

```python
from wiverno.main import Wiverno
from wiverno.templating.templator import Templator

app = Wiverno()
templator = Templator()

@app.get("/")
def index(request):
    html = templator.render("index.html", {
        "title": "Home",
        "message": "Welcome!"
    })
    return "200 OK", html
```

### With Class-Based Views

```python
from wiverno.main import Wiverno
from wiverno.views.base_views import BaseView

class APIView(BaseView):
    def get(self, request):
        return "200 OK", '{"status": "ok"}'

    def post(self, request):
        return "201 Created", '{"created": true}'

app = Wiverno(routes_list=[
    ("/api", APIView),
])
```

## Error Handling

The application automatically handles common HTTP errors:

- **404 Not Found** - When no route matches
- **405 Method Not Allowed** - When route exists but method is not supported
- **500 Internal Server Error** - When an exception occurs in a view

You can customize error handling by providing custom handler functions via the `page_404`, `page_405`, and `page_500` constructor parameters. Default error handlers use built-in templates from the framework.

## WSGI Compatibility

Wiverno applications are fully WSGI-compatible and can be deployed with any WSGI server:

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
serve(app, host='0.0.0.0', port=8000)
```

## See Also

- [Router](router.md) - URL routing and pattern matching
- [Request](requests.md) - Request handling
- [RunServer](server.md) - Development server
