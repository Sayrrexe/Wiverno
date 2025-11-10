# Architecture

Wiverno's internal architecture.

## WSGI Flow

HTTP Request → WSGI environ dict → Request parsing → Route matching → Handler execution → WSGI response

## Components

### Wiverno (Main WSGI App)

Entry point implementing WSGI interface:

- Initialize router with routes
- Parse WSGI environ
- Route requests to handlers
- Generate responses
- Handle errors (404, 405, 500)

### Request (Request Parsing)

Parses WSGI environ into Request object:

```python
request.method      # HTTP method (GET, POST, etc)
request.path        # Normalized URL path
request.query_params  # Parsed query string dict
request.data        # Parsed request body
request.headers     # HTTP headers dict
request.cookies     # Parsed cookies dict
```

Auto-parses body based on Content-Type:
- `application/json` - JSON decode
- `application/x-www-form-urlencoded` - form parsing
- `multipart/form-data` - file upload parsing

### Router (Route Matching)

Matches request path to handlers:

```python
@app.get("/users")
def list_users(request):
    return "200 OK", "response"

@app.post("/users")
def create_user(request):
    return "201 CREATED", "created"
```

Path normalization: trailing slashes removed except "/"

Route matching returns `(handler, path_params)` tuple

### Handler Response Contract

All handlers must return `(status_string, html_body)` tuple:

```python
def handler(request: Request) -> tuple[str, str]:
    return "200 OK", "<html>...</html>"
```

Valid status strings: "200 OK", "404 NOT FOUND", "201 CREATED", etc.

## Error Handling

Three customizable error handlers:

```python
app = Wiverno(
    page_404=custom_404_handler,   # Route not found
    page_405=custom_405_handler,   # Method not allowed
    page_500=custom_500_handler,   # Server error
)
```

Each receives Request object; 500 handler gets traceback in debug mode.

## Class-Based Views

Use BaseView for multiple HTTP methods:

```python
from wiverno.views.base_views import BaseView

class UserView(BaseView):
    def get(self, request):
        return "200 OK", "list"

    def post(self, request):
        return "201 CREATED", "created"

app.route("/users")(UserView())
```

Methods dispatched by `request.method.lower()`

## Modular Routing

Router class for organizing routes:

```python
from wiverno.core.router import Router

api_router = Router()

@api_router.get("/data")
def api_data(request):
    return "200 OK", "data"

app.include_router(api_router, prefix="/api")
# Route becomes /api/data
```

## Module Structure

```
wiverno/
├── main.py              # Wiverno WSGI app
├── cli.py               # CLI commands
├── core/
│   ├── requests.py      # Request parsing
│   ├── router.py        # Router class
│   └── server.py        # WSGI server
├── templating/
│   └── templator.py     # Jinja2 wrapper
├── views/
│   ├── base_views.py    # BaseView class
│   └── pages_errors.py  # Error handlers
└── dev/
    └── dev_server.py    # Dev server with hot reload
```

## Next Steps

- [Testing](testing.md) - Writing tests
- [Code Style](code-style.md) - Code standards
- [Workflow](workflow.md) - Development workflow
- [Contributing](contributing.md) - Contribution guidelines
