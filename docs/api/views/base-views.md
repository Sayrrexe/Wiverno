# Base Views

The `BaseView` class provides a foundation for creating class-based views in Wiverno. It automatically dispatches requests to methods based on HTTP method.

## Module: `wiverno.views.base_views`

## Overview

Class-based views are an alternative to function-based views. They allow you to organize view logic in classes with methods for different HTTP methods:

- **GET** - `get(request)`
- **POST** - `post(request)`
- **PUT** - `put(request)`
- **DELETE** - `delete(request)`
- **PATCH** - `patch(request)`
- Other HTTP methods - `connect(request)`, `head(request)`, `options(request)`, `trace(request)`

## Basic Usage

```python
from wiverno.main import Wiverno
from wiverno.views.base_views import BaseView
from wiverno.core.requests import Request

class ItemsView(BaseView):
    def get(self, request: Request) -> tuple[str, str]:
        return "200 OK", "List of items"

    def post(self, request: Request) -> tuple[str, str]:
        return "201 CREATED", "Item created"

app = Wiverno()
app.route("/items")(ItemsView())
```

## Class Definition

### `BaseView`

Base class for class-based views.

```python
from wiverno.views.base_views import BaseView

class MyView(BaseView):
    """Define methods for each HTTP method you want to handle."""

    def get(self, request):
        return "200 OK", "GET response"

    def post(self, request):
        return "201 CREATED", "POST response"
```

## Methods

### HTTP Method Handlers

Define methods named after HTTP methods (lowercase) to handle requests:

#### `get(request) -> tuple[str, str]`

Handle GET requests.

```python
class UserListView(BaseView):
    def get(self, request):
        return "200 OK", "Users list"
```

#### `post(request) -> tuple[str, str]`

Handle POST requests.

```python
class UserListView(BaseView):
    def post(self, request):
        # request.data contains POST body
        name = request.data.get('name')
        return "201 CREATED", f"User {name} created"
```

#### `put(request) -> tuple[str, str]`

Handle PUT requests (full resource replacement).

```python
class UserDetailView(BaseView):
    def put(self, request):
        # request.data contains new resource data
        return "200 OK", "User updated"
```

#### `patch(request) -> tuple[str, str]`

Handle PATCH requests (partial resource update).

```python
class UserDetailView(BaseView):
    def patch(self, request):
        # request.data contains partial update
        return "200 OK", "User partially updated"
```

#### `delete(request) -> tuple[str, str]`

Handle DELETE requests.

```python
class UserDetailView(BaseView):
    def delete(self, request):
        return "204 NO CONTENT", ""
```

#### `connect(request)`, `head(request)`, `options(request)`, `trace(request)`

Handle other HTTP methods.

```python
class ResourceView(BaseView):
    def head(self, request):
        return "200 OK", ""

    def options(self, request):
        return "200 OK", "GET,POST,PUT,DELETE"
```

### `__call__(request) -> tuple[str, str]`

The magic method that makes the view callable. Automatically dispatches to the appropriate HTTP method handler.

**Parameters:**

- `request` (Request): The incoming request object

**Returns:** `tuple[str, str]` - (status_string, html_body)

**Raises:**

- Returns 405 Method Not Allowed if the method handler is not implemented

This method is called automatically by Wiverno and typically doesn't need to be called directly.

```python
view = MyView()
status, body = view(request)  # Calls get/post/etc based on request.method
```

## Request Dispatching

`BaseView` automatically routes requests to methods based on `request.method`:

```python
class APIView(BaseView):
    def get(self, request):
        return "200 OK", "GET response"

    def post(self, request):
        return "201 CREATED", "POST response"

# When request.method == "GET", get() is called
# When request.method == "POST", post() is called
# When request.method == "PUT", 405 is returned (not implemented)
```

## Error Handling

If the HTTP method is not implemented, BaseView automatically returns a 405 Method Not Allowed response:

```python
class GetOnlyView(BaseView):
    def get(self, request):
        return "200 OK", "Data"

    # PUT, POST, DELETE not implemented
    # POST request will return 405

view = GetOnlyView()
request.method = "POST"
status, body = view(request)
# status == "405 METHOD NOT ALLOWED"
```

## Registration with Application

### Using Decorator

Register a class-based view using the `@app.route()` or HTTP method decorators:

```python
from wiverno.main import Wiverno
from wiverno.views.base_views import BaseView

app = Wiverno()

class UserView(BaseView):
    def get(self, request):
        return "200 OK", "Users"

    def post(self, request):
        return "201 CREATED", "User created"

# Register the instantiated view
app.route("/users")(UserView())
```

### Using routes_list

Include class-based views in the routes list:

```python
class ArticleView(BaseView):
    def get(self, request):
        return "200 OK", "Articles"

    def post(self, request):
        return "201 CREATED", "Article created"

app = Wiverno(routes_list=[
    ("/articles", ArticleView),
])
```

### With Router

Use class-based views with routers:

```python
from wiverno.core.router import Router

router = Router()

class ItemView(BaseView):
    def get(self, request):
        return "200 OK", "Items"

router.route("/items")(ItemView())

app.include_router(router, prefix="/api")
```

## Usage Examples

### Simple GET and POST Handler

```python
from wiverno.views.base_views import BaseView
from wiverno.core.requests import Request

class ContactView(BaseView):
    def get(self, request: Request) -> tuple[str, str]:
        return "200 OK", """
            <form method="POST">
                <input type="text" name="message">
                <button>Send</button>
            </form>
        """

    def post(self, request: Request) -> tuple[str, str]:
        message = request.data.get('message')
        return "200 OK", f"Message received: {message}"

# Register
app.route("/contact")(ContactView())
```

### REST API Endpoint

```python
class ArticleView(BaseView):
    def get(self, request: Request) -> tuple[str, str]:
        # Get all articles
        return "200 OK", '[{"id": 1, "title": "First"}]'

    def post(self, request: Request) -> tuple[str, str]:
        # Create new article
        data = request.data
        title = data.get('title')
        return "201 CREATED", f'{{"title": "{title}"}}'

    def put(self, request: Request) -> tuple[str, str]:
        # Update article
        return "200 OK", '{"updated": true}'

    def delete(self, request: Request) -> tuple[str, str]:
        # Delete article
        return "204 NO CONTENT", ""

app.route("/articles")(ArticleView())
```

### Combining with Templates

```python
from wiverno.templating.templator import Templator

class ProfileView(BaseView):
    def __init__(self):
        self.templator = Templator()

    def get(self, request: Request) -> tuple[str, str]:
        user_id = request.query_params.get('id')
        html = self.templator.render("profile.html", {
            "user_id": user_id
        })
        return "200 OK", html

    def post(self, request: Request) -> tuple[str, str]:
        # Update profile
        return "200 OK", "Profile updated"

app.route("/profile")(ProfileView())
```

### API Validation

```python
import json

class DataAPIView(BaseView):
    def get(self, request: Request) -> tuple[str, str]:
        return "200 OK", json.dumps({"status": "ok"})

    def post(self, request: Request) -> tuple[str, str]:
        # Validate request data
        required_fields = {'name', 'email'}
        provided_fields = set(request.data.keys())

        if not required_fields.issubset(provided_fields):
            return "400 BAD REQUEST", "Missing required fields"

        # Process data
        return "201 CREATED", json.dumps({"created": True})

    def put(self, request: Request) -> tuple[str, str]:
        if not request.data:
            return "400 BAD REQUEST", "Empty body"

        return "200 OK", json.dumps({"updated": True})

app.route("/api/data")(DataAPIView())
```

### Using Class State

```python
class CacheView(BaseView):
    def __init__(self):
        self.cache = {}

    def get(self, request: Request) -> tuple[str, str]:
        key = request.query_params.get('key')
        if key in self.cache:
            return "200 OK", self.cache[key]
        return "404 NOT FOUND", "Not found"

    def post(self, request: Request) -> tuple[str, str]:
        key = request.data.get('key')
        value = request.data.get('value')
        self.cache[key] = value
        return "201 CREATED", "Cached"

cache_view = CacheView()
app.route("/cache")(cache_view)
```

### Multi-Action View

```python
class AdminDashboardView(BaseView):
    def get(self, request: Request) -> tuple[str, str]:
        action = request.query_params.get('action', 'overview')

        if action == 'overview':
            return "200 OK", "Dashboard overview"
        elif action == 'users':
            return "200 OK", "User management"
        elif action == 'settings':
            return "200 OK", "Settings"
        else:
            return "400 BAD REQUEST", "Invalid action"

    def post(self, request: Request) -> tuple[str, str]:
        action = request.data.get('action')

        if action == 'save_settings':
            return "200 OK", "Settings saved"
        elif action == 'create_user':
            return "201 CREATED", "User created"
        else:
            return "400 BAD REQUEST", "Invalid action"

app.route("/admin")(AdminDashboardView())
```

## Comparison: Function-Based vs Class-Based

### Function-Based View

```python
@app.route("/items", methods=["GET", "POST"])
def items_view(request):
    if request.method == "GET":
        return "200 OK", "Items list"
    elif request.method == "POST":
        return "201 CREATED", "Item created"
```

### Class-Based View

```python
class ItemsView(BaseView):
    def get(self, request):
        return "200 OK", "Items list"

    def post(self, request):
        return "201 CREATED", "Item created"

app.route("/items")(ItemsView())
```

Class-based views are cleaner when handling multiple HTTP methods for the same resource.

## See Also

- [Application](../core/application.md) - Wiverno application class
- [Request](../core/requests.md) - Request handling
- [Router](../core/router.md) - URL routing
