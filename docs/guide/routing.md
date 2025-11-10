# Routing

Learn how to define and organize routes in your Wiverno application.

## Overview

Wiverno provides flexible routing through decorators and explicit route lists. Routes map URL patterns to view functions or classes.

## Basic Routing

### Using Decorators (Recommended)

The recommended way to define routes is using decorators:

```python
from wiverno.main import Wiverno

app = Wiverno()

@app.route("/")
def index(request):
    """Homepage view."""
    return "200 OK", "Welcome!"

@app.get("/users")
def users_list(request):
    """List all users - GET only."""
    return "200 OK", "User list"

@app.post("/users")
def create_user(request):
    """Create user - POST only."""
    return "201 CREATED", "User created"
```

## HTTP Methods

### Method-Specific Decorators

Wiverno provides decorators for common HTTP methods:

```python
@app.get("/items")
def list_items(request):
    """Handle GET requests."""
    return "200 OK", "Items list"

@app.post("/items")
def create_item(request):
    """Handle POST requests."""
    return "201 CREATED", "Item created"

@app.put("/items")
def update_item(request):
    """Handle PUT requests."""
    item_id = request.query_params.get("id")
    return "200 OK", f"Updated item {item_id}"

@app.delete("/items")
def delete_item(request):
    """Handle DELETE requests."""
    item_id = request.query_params.get("id")
    return "204 NO CONTENT", ""

@app.patch("/items")
def patch_item(request):
    """Handle PATCH requests."""
    return "200 OK", "Item patched"
```

### Custom Method Lists

Specify allowed methods explicitly:

```python
@app.route("/api/data", methods=["GET", "POST", "PUT"])
def handle_data(request):
    """Handle multiple HTTP methods."""
    if request.method == "GET":
        return "200 OK", "Data retrieved"
    elif request.method == "POST":
        return "201 CREATED", "Data created"
    elif request.method == "PUT":
        return "200 OK", "Data updated"
```

## Path Parameters

Wiverno uses static path matching - routes are matched exactly as defined. Dynamic path parameters (like `/user/<id>`) are not currently supported.

For dynamic content based on URL segments, use query parameters instead:

### Using Query Parameters

Extract values from query strings:

```python
@app.get("/user")
def user_detail(request):
    """Get user by ID from query parameter."""
    user_id = request.query_params.get("id")
    if user_id:
        return "200 OK", f"User ID: {user_id}"
    return "200 OK", "Please provide user ID"

# Usage: /user?id=123
# request.query_params = {"id": "123"}
```

### Multiple Query Parameters

Handle multiple query parameters:

```python
@app.get("/search")
def search(request):
    """Search with multiple parameters."""
    query = request.query_params.get("q", "")
    limit = request.query_params.get("limit", "10")
    offset = request.query_params.get("offset", "0")
    return "200 OK", f"Search: {query}, Limit: {limit}, Offset: {offset}"

# Usage: /search?q=python&limit=20&offset=10
```

## Using Route Lists

For simple applications or when migrating, you can use route lists:

```python
from wiverno.main import Wiverno

def index(request):
    """Homepage view."""
    return "200 OK", "Welcome to Wiverno!"

def about(request):
    """About page view."""
    return "200 OK", "About Us"

app = Wiverno(routes_list=[
    ("/", index),
    ("/about", about),
])
```

However, **decorators are preferred** for better code organization.

## Using Router Class

For modular applications, use the `Router` class:

```python
from wiverno.core.router import Router
from wiverno.main import Wiverno

# Create a router for API endpoints
api_router = Router()

@api_router.get("/users")
def api_users(request):
    """API: List users."""
    return "200 OK", '{"users": []}'

@api_router.post("/users")
def api_create_user(request):
    """API: Create user."""
    return "201 CREATED", '{"id": 1}'

@api_router.get("/users/detail")
def api_user_detail(request):
    """API: Get user details."""
    user_id = request.query_params.get("id")
    return "200 OK", f'{{"id": {user_id}}}'

# Create app and include router
app = Wiverno()
app.include_router(api_router, prefix="/api/v1")
```

### Router with Prefix

Organize routes by feature:

```python
# Blog routes
blog_router = Router()

@blog_router.get("/")
def blog_index(request):
    """Blog homepage."""
    return "200 OK", "Blog posts"

@blog_router.get("/post")
def blog_post(request):
    """Single blog post."""
    slug = request.query_params.get("slug")
    return "200 OK", f"Post: {slug}"

# Admin routes
admin_router = Router()

@admin_router.get("/dashboard")
def admin_dashboard(request):
    """Admin dashboard."""
    return "200 OK", "Admin Dashboard"

# Combine in app
app = Wiverno()
app.include_router(blog_router, prefix="/blog")
app.include_router(admin_router, prefix="/admin")

# Routes:
# /blog/ -> blog_index
# /blog/post?slug=my-post -> blog_post
# /admin/dashboard -> admin_dashboard
```

## Path Normalization

Wiverno automatically normalizes paths:

```python
# These are all equivalent:
@app.route("/users")
@app.route("/users/")
@app.route("users")
@app.route("users/")

# All match: /users (trailing slash removed)
```

Root path is special:

```python
@app.route("/")  # Homepage - keeps the single slash
```

## Route Priority

Routes are matched exactly as defined. More specific paths should be defined first to take precedence:

```python
# Define more specific routes first
@app.get("/users/admin")  # Specific route for admin
def admin_users(request):
    return "200 OK", "Admin users"

@app.get("/users")  # General users route
def user_detail(request):
    return "200 OK", "User detail"

# /users/admin -> admin_users
# /users -> user_detail
# /users/123 -> 404 (not found - no pattern matching)
```

## Class-Based Views with Routes

Use class-based views for better organization:

```python
from wiverno.views.base_views import BaseView

class UserView(BaseView):
    """Handle user operations."""

    def get(self, request):
        """List users or get user by ID."""
        user_id = request.query_params.get("id")
        if user_id:
            return "200 OK", f"User {user_id}"
        return "200 OK", "User list"

    def post(self, request):
        """Create new user."""
        return "201 CREATED", "User created"

    def put(self, request):
        """Update user."""
        user_id = request.query_params.get("id")
        return "200 OK", f"User {user_id} updated"

    def delete(self, request):
        """Delete user."""
        return "204 NO CONTENT", ""

# Register class-based view
app = Wiverno(routes_list=[
    ("/users", UserView()),
])
```

## Error Handling

### 404 Not Found

Automatically handled when no route matches:

```python
# Request to /nonexistent returns 404
```

### 405 Method Not Allowed

When route exists but method is not allowed:

```python
@app.get("/users")
def users(request):
    return "200 OK", "Users"

# POST /users returns 405
```

### Custom Error Handlers

Provide custom error pages:

```python
def custom_404(request):
    """Custom 404 handler."""
    return "404 NOT FOUND", "<h1>Page Not Found</h1>"

def custom_405(request):
    """Custom 405 handler."""
    return "405 METHOD NOT ALLOWED", "<h1>Method Not Allowed</h1>"

app = Wiverno(
    routes_list=routes,
    page_404=custom_404,
    page_405=custom_405,
)
```

## Best Practices

### 1. Organize by Feature

```python
# users.py
users_router = Router()

@users_router.get("/")
def list_users(request):
    pass

@users_router.post("/")
def create_user(request):
    pass

# posts.py
posts_router = Router()

@posts_router.get("/")
def list_posts(request):
    pass

# main.py
app = Wiverno()
app.include_router(users_router, prefix="/users")
app.include_router(posts_router, prefix="/posts")
```

### 2. Use Descriptive Names

```python
# Good
@app.get("/users/posts")
def get_user_post(request):
    user_id = request.query_params.get("user_id")
    post_id = request.query_params.get("post_id")
    pass

# Bad
@app.get("/users/posts")
def handler(request):
    pass
```

### 3. RESTful Design

```python
# Resources: /users
@app.get("/users")          # List all users
@app.post("/users")         # Create user
@app.get("/users/detail")   # Get single user (use query param for id)
@app.put("/users/detail")   # Update user (use query param for id)
@app.delete("/users/detail")# Delete user (use query param for id)
```

### 4. Version Your API

```python
api_v1 = Router()
# ... define v1 routes

api_v2 = Router()
# ... define v2 routes

app.include_router(api_v1, prefix="/api/v1")
app.include_router(api_v2, prefix="/api/v2")
```

## Next Steps

- [Requests](requests.md) - Handle request data
- [Class-Based Views](../api/views/base-views.md) - Class-based views
- [API Reference](../api/index.md) - Complete API reference
