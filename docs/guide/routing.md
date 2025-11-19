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

Wiverno supports dynamic path parameters with FastAPI-style syntax and automatic type conversion.

### Basic Path Parameters

Define path parameters using curly braces:

```python
@app.get("/users/{id}")
def user_detail(request):
    """Get user by ID from path parameter."""
    user_id = request.path_params["id"]  # String by default
    return "200 OK", f"<h1>User: {user_id}</h1>"

# Usage: /users/123
# request.path_params = {"id": "123"}
```

### Typed Path Parameters

Add type hints for automatic conversion:

```python
@app.get("/users/{id:int}")
def get_user(request):
    """Get user with integer ID."""
    user_id = request.path_params["id"]  # Already converted to int
    return "200 OK", f"<h1>User ID: {user_id}</h1>"

@app.get("/products/{price:float}")
def get_product_by_price(request):
    """Get products by price."""
    price = request.path_params["price"]  # Already converted to float
    return "200 OK", f"<p>Price: ${price:.2f}</p>"

# Usage: /users/123 -> user_id = 123 (int)
# Usage: /products/19.99 -> price = 19.99 (float)
```

### Supported Parameter Types

- `{name}` - String parameter (default, matches `[^/]+`)
- `{name:str}` - Explicit string parameter
- `{name:int}` - Integer parameter (matches `[0-9]+`)
- `{name:float}` - Float parameter (matches `[0-9]+\.?[0-9]*`)
- `{name:path}` - Path parameter (matches `.+`, includes slashes)

### Multiple Path Parameters

Combine multiple parameters in one route:

```python
@app.get("/posts/{slug}/comments/{comment_id:int}")
def get_comment(request):
    """Get comment from specific post."""
    slug = request.path_params["slug"]           # str
    comment_id = request.path_params["comment_id"]  # int
    return "200 OK", f"<p>Post: {slug}, Comment: {comment_id}</p>"

# Usage: /posts/hello-world/comments/42
# request.path_params = {"slug": "hello-world", "comment_id": 42}
```

### Path Parameter for File Paths

Use `:path` type to capture paths with slashes:

```python
@app.get("/files/{filepath:path}")
def serve_file(request):
    """Serve file from nested path."""
    filepath = request.path_params["filepath"]  # Can contain slashes
    return "200 OK", f"<p>File: {filepath}</p>"

# Usage: /files/docs/guide/intro.md
# request.path_params = {"filepath": "docs/guide/intro.md"}
```

### Using Query Parameters

Query parameters work alongside path parameters:

```python
@app.get("/users/{id:int}/posts")
def user_posts(request):
    """Get user's posts with pagination."""
    user_id = request.path_params["id"]          # From path
    limit = request.query_params.get("limit", "10")   # From query string
    offset = request.query_params.get("offset", "0")
    return "200 OK", f"<p>User {user_id}: Posts (limit={limit}, offset={offset})</p>"

# Usage: /users/42/posts?limit=20&offset=10
```

### Multiple Query Parameter Values

Use `getlist()` for repeated query parameters:

```python
@app.get("/search")
def search(request):
    """Search with multiple tags."""
    tags = request.query_params.getlist("tag")  # Get all tag values
    query = request.query_params.get("q", "")
    return "200 OK", f"<p>Search: {query}, Tags: {', '.join(tags)}</p>"

# Usage: /search?q=python&tag=web&tag=framework&tag=wsgi
# request.query_params.getlist("tag") = ["web", "framework", "wsgi"]
```

## Using Router Class

For modular applications, use the `Router` class:

```python
from wiverno.core.routing.router import Router
from wiverno import Wiverno

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

@api_router.get("/users/{id:int}")
def api_user_detail(request):
    """API: Get user details."""
    user_id = request.path_params["id"]  # int from path
    return "200 OK", f'{{"id": {user_id}}}'

# Create app and include router
app = Wiverno()
app.include_router(api_router, prefix="/api/v1")

# Routes become:
# GET  /api/v1/users
# POST /api/v1/users
# GET  /api/v1/users/{id:int}
```

### Router with Prefix

Organize routes by feature:

```python
# Blog routes
blog_router = Router()

@blog_router.get("/")
def blog_index(request):
    """Blog homepage."""
    return "200 OK", "<h1>Blog posts</h1>"

@blog_router.get("/{slug}")
def blog_post(request):
    """Single blog post."""
    slug = request.path_params["slug"]
    return "200 OK", f"<h1>Post: {slug}</h1>"

@blog_router.get("/{slug}/comments/{comment_id:int}")
def blog_comment(request):
    """Single comment on a blog post."""
    slug = request.path_params["slug"]
    comment_id = request.path_params["comment_id"]
    return "200 OK", f"<p>Comment {comment_id} on {slug}</p>"

# Admin routes
admin_router = Router()

@admin_router.get("/dashboard")
def admin_dashboard(request):
    """Admin dashboard."""
    return "200 OK", "<h1>Admin Dashboard</h1>"

@admin_router.get("/users/{id:int}")
def admin_user(request):
    """Admin user details."""
    user_id = request.path_params["id"]
    return "200 OK", f"<h1>Admin: User {user_id}</h1>"

# Combine in app
app = Wiverno()
app.include_router(blog_router, prefix="/blog")
app.include_router(admin_router, prefix="/admin")

# Routes:
# /blog/ -> blog_index
# /blog/my-first-post -> blog_post
# /blog/my-first-post/comments/5 -> blog_comment
# /admin/dashboard -> admin_dashboard
# /admin/users/42 -> admin_user
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

Routes are matched with intelligent priority:

### Static Routes Take Precedence

Static routes (without parameters) are checked first with O(1) lookup:

```python
@app.get("/users/admin")  # Static route - checked first
def admin_users(request):
    return "200 OK", "<h1>Admin users</h1>"

@app.get("/users/{id:int}")  # Dynamic route - checked after static
def user_detail(request):
    user_id = request.path_params["id"]
    return "200 OK", f"<h1>User {user_id}</h1>"

# /users/admin -> admin_users (static route wins)
# /users/123 -> user_detail (dynamic route matches)
```

### Dynamic Route Specificity

Dynamic routes are sorted by specificity (more segments = higher priority):

```python
@app.get("/posts/{slug}/comments/{id:int}")  # 4 segments - higher priority
def post_comment(request):
    slug = request.path_params["slug"]
    comment_id = request.path_params["id"]
    return "200 OK", f"<p>Comment {comment_id} on {slug}</p>"

@app.get("/posts/{slug}")  # 2 segments - lower priority
def post_detail(request):
    slug = request.path_params["slug"]
    return "200 OK", f"<h1>Post: {slug}</h1>"

# /posts/hello-world/comments/5 -> post_comment (more specific)
# /posts/hello-world -> post_detail
```

### Route Conflict Detection

Registering the same path+method twice raises an error:

```python
@app.get("/users")
def users1(request):
    return "200 OK", "Users v1"

@app.get("/users")  # ❌ Raises RouteConflictError
def users2(request):
    return "200 OK", "Users v2"
```

## Class-Based Views with Routes

Use class-based views for better organization:

```python
from wiverno.views.base_views import BaseView
from wiverno import Wiverno

class UserView(BaseView):
    """Handle user operations."""

    def get(self, request):
        """Get user by ID."""
        user_id = request.path_params["id"]
        return "200 OK", f"<h1>User {user_id}</h1>"

    def put(self, request):
        """Update user."""
        user_id = request.path_params["id"]
        return "200 OK", f"<p>User {user_id} updated</p>"

    def delete(self, request):
        """Delete user."""
        return "204 NO CONTENT", ""

class UserListView(BaseView):
    """Handle user list operations."""

    def get(self, request):
        """List all users."""
        return "200 OK", "<ul><li>User 1</li><li>User 2</li></ul>"

    def post(self, request):
        """Create new user."""
        return "201 CREATED", "<p>User created</p>"

# Register class-based views
app = Wiverno()
app.route("/users")(UserListView())
app.route("/users/{id:int}")(UserView())
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
class Custom404:
    def __call__(self, request):
        """Custom 404 handler."""
        return "404 NOT FOUND", "<h1>Page Not Found</h1>"

class Custom405:
    def __call__(self, request):
        """Custom 405 handler."""
        method = request.method
        return "405 METHOD NOT ALLOWED", f"<h1>Method {method} Not Allowed</h1>"

class Custom500:
    def __call__(self, request, error_traceback=None):
        """Custom 500 handler."""
        return "500 INTERNAL SERVER ERROR", "<h1>Server Error</h1>"

app = Wiverno(
    page_404=Custom404(),
    page_405=Custom405(),
    page_500=Custom500()
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
@app.get("/users/{user_id:int}/posts/{post_id:int}")
def get_user_post(request):
    user_id = request.path_params["user_id"]
    post_id = request.path_params["post_id"]
    return "200 OK", f"<h1>User {user_id}, Post {post_id}</h1>"

# Bad
@app.get("/users/{user_id:int}/posts/{post_id:int}")
def handler(request):
    pass
```

### 3. RESTful Design

```python
# Resources: /users
@app.get("/users")               # List all users
@app.post("/users")              # Create user
@app.get("/users/{id:int}")      # Get single user
@app.put("/users/{id:int}")      # Update user
@app.delete("/users/{id:int}")   # Delete user

# Nested resources: /users/{user_id}/posts
@app.get("/users/{user_id:int}/posts")              # List user's posts
@app.post("/users/{user_id:int}/posts")             # Create post for user
@app.get("/users/{user_id:int}/posts/{post_id:int}")# Get specific post
@app.put("/users/{user_id:int}/posts/{post_id:int}")# Update post
@app.delete("/users/{user_id:int}/posts/{post_id:int}")# Delete post
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
