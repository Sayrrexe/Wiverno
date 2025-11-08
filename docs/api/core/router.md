# Router

The `Router` class provides a way to organize and group routes separately from the main `Wiverno` application. Routes defined in a router can be included in a Wiverno application using `include_router()`.

## Module: `wiverno.core.router`

## Overview

Routers are useful for organizing your application into logical modules:

- **API routes** - Group API endpoints
- **Admin routes** - Separate admin functionality
- **Feature modules** - Organize routes by feature

Routes from a router are included in the main application with an optional URL prefix.

## Basic Usage

```python
from wiverno.core.router import Router

# Create a router
api_router = Router()

# Define routes
@api_router.get("/users")
def list_users(request):
    return "200 OK", "Users list"

@api_router.post("/users")
def create_user(request):
    return "201 CREATED", "User created"

# Include in main app
from wiverno.main import Wiverno

app = Wiverno()
app.include_router(api_router, prefix="/api")

# Routes become:
# GET /api/users
# POST /api/users
```

## Constructor

### `Router()`

Creates a new empty router with no routes.

```python
router = Router()
```

## Methods

### Decorator Methods

#### `@router.route(path, methods=None)`

Generic route decorator for specifying custom HTTP methods.

**Parameters:**

- `path` (str): URL path for the route
- `methods` (list[str], optional): List of allowed HTTP methods. If `None`, all methods are allowed.

```python
@router.route("/data", methods=["GET", "POST"])
def handle_data(request):
    return "200 OK", "Data"
```

#### `@router.get(path)`, `@router.post(path)`, `@router.put(path)`, `@router.patch(path)`, `@router.delete(path)`

HTTP method-specific decorators.

```python
@router.get("/items")
def list_items(request):
    return "200 OK", "Items"

@router.post("/items")
def create_item(request):
    return "201 CREATED", "Item created"

@router.put("/items/1")
def update_item(request):
    return "200 OK", "Item updated"

@router.delete("/items/1")
def delete_item(request):
    return "204 NO CONTENT", ""
```

#### `@router.connect(path)`, `@router.head(path)`, `@router.options(path)`, `@router.trace(path)`

Additional HTTP method decorators for CONNECT, HEAD, OPTIONS, and TRACE.

### Programmatic Route Addition

#### `router.add_route(path, handler, methods=None)`

Programmatically add a route to the router without using decorators.

**Parameters:**

- `path` (str): URL path for the route
- `handler` (Callable): Function to handle the route
- `methods` (list[str], optional): Allowed HTTP methods. If `None`, no method restriction.

**Returns:** None

```python
def api_status(request):
    return "200 OK", '{"status": "ok"}'

router.add_route("/status", api_status, methods=["GET"])
```

### Route Retrieval

#### `router.get_routes() -> list[dict]`

Returns all registered routes in the router.

**Returns:** List of route dictionaries with keys:
- `path` (str): Route path
- `handler` (Callable): Handler function
- `methods` (list[str] | None): Allowed HTTP methods

```python
router = Router()

@router.get("/data")
def get_data(request):
    return "200 OK", "Data"

routes = router.get_routes()
print(routes)
# Output: [{'path': '/data', 'handler': <function>, 'methods': ['GET']}]
```

## Integration with Wiverno

### Including Routers

Use `app.include_router()` to add router routes to your Wiverno application.

```python
from wiverno.main import Wiverno
from wiverno.core.router import Router

# Create routers
api_router = Router()
admin_router = Router()

# Define routes in routers
@api_router.get("/users")
def api_users(request):
    return "200 OK", "API Users"

@admin_router.get("/dashboard")
def admin_dashboard(request):
    return "200 OK", "Admin Dashboard"

# Create main app and include routers
app = Wiverno()
app.include_router(api_router, prefix="/api")
app.include_router(admin_router, prefix="/admin")

# Final routes:
# GET /api/users
# GET /admin/dashboard
```

### Path Normalization

Paths in routers follow the same normalization rules as the main application:

- Trailing slashes are removed except for `/`
- `/users/` becomes `/users`
- `/` stays `/`

```python
@router.get("/users")      # Accessible at /users
@router.get("/users/")     # Also accessible at /users (slash removed)
@router.get("/")           # Root route, stays as /
```

### Method Restrictions

If no methods are specified in the router, no method restriction is applied when the route is included in the application.

```python
@router.route("/data")  # No methods specified
def handle_data(request):
    return "200 OK", "Data"

# This route accepts ALL HTTP methods
```

If methods are specified in the router, they are preserved when included in the application.

```python
@router.get("/users")  # Only GET allowed
def get_users(request):
    return "200 OK", "Users"
```

## Examples

### API Router

```python
from wiverno.core.router import Router
from wiverno.core.requests import Request

api_router = Router()

@api_router.get("/posts")
def list_posts(request: Request):
    return "200 OK", '[{"id": 1, "title": "First"}]'

@api_router.post("/posts")
def create_post(request: Request):
    data = request.data
    title = data.get('title')
    return "201 CREATED", f'{{"title": "{title}"}}'

@api_router.get("/posts/1")
def get_post(request: Request):
    return "200 OK", '{"id": 1, "title": "First"}'
```

### Nested Router Prefixes

```python
from wiverno.core.router import Router
from wiverno.main import Wiverno

# V1 API routes
v1_router = Router()

@v1_router.get("/users")
def v1_users(request):
    return "200 OK", "V1 Users"

# V2 API routes
v2_router = Router()

@v2_router.get("/users")
def v2_users(request):
    return "200 OK", "V2 Users"

# Include with nested prefixes
app = Wiverno()
app.include_router(v1_router, prefix="/api/v1")
app.include_router(v2_router, prefix="/api/v2")

# Routes:
# GET /api/v1/users
# GET /api/v2/users
```

### Admin Routes

```python
admin_router = Router()

@admin_router.get("/users")
def admin_users(request):
    return "200 OK", "Admin User List"

@admin_router.post("/users")
def admin_create_user(request):
    return "201 CREATED", "User created"

@admin_router.get("/settings")
def admin_settings(request):
    return "200 OK", "Admin Settings"

# Include with /admin prefix
app.include_router(admin_router, prefix="/admin")
```

## See Also

- [Application](application.md) - Main Wiverno application class
- [Request](requests.md) - Request handling
- [Base Views](../views/base-views.md) - Class-based views
