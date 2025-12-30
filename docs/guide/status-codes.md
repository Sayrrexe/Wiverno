# HTTP Status Codes

Understanding how to work with HTTP status codes in Wiverno.

## Overview

Wiverno provides flexible ways to specify HTTP status codes in your view functions. The framework automatically normalizes all status codes to the proper WSGI format (`"200 OK"`, `"404 Not Found"`, etc.) internally, regardless of how you specify them.

## Supported Formats

You can use any of the following formats when returning status codes from your views:

### 1. Integer Status Code

The simplest and **recommended** approach for non-200 responses:

```python
@app.post("/users")
def create_user(request):
    """Create a new user."""
    return 201, "User created"

@app.delete("/users/{id:int}")
def delete_user(request):
    """Delete a user."""
    return 204, ""

@app.get("/admin")
def admin_panel(request):
    """Protected endpoint."""
    if not is_authenticated(request):
        return 401, "Unauthorized"
    return "Admin panel"
```

**Benefits:**

- Clean and concise
- Type-safe (can't make typos in status phrases)
- Easy to read

### 2. String with Status Code Only

You can provide just the numeric code as a string:

```python
@app.post("/users")
def create_user(request):
    """Create a new user."""
    return "201", "User created"

@app.get("/protected")
def protected(request):
    """Protected resource."""
    return "403", "Forbidden"
```

Wiverno will automatically add the correct status phrase (`"201 Created"`, `"403 Forbidden"`).

### 3. Full Status String

You can also provide the complete status line:

```python
@app.post("/users")
def create_user(request):
    """Create a new user."""
    return "201 Created", "User created"

@app.delete("/users/{id:int}")
def delete_user(request):
    """Delete a user."""
    return "204 No Content", ""
```

**Note:** If you provide an incorrect phrase (e.g., `"201 Wrong"`), Wiverno will automatically correct it to the standard phrase (`"201 Created"`).

### 4. Omitting Status Code (200 OK)

For successful responses (200 OK), you can omit the status code entirely:

```python
@app.get("/")
def index(request):
    """Homepage - returns 200 OK by default."""
    return "Hello, World!"

@app.get("/about")
def about(request):
    """About page - returns 200 OK by default."""
    return "<h1>About Us</h1>"
```

This is the **recommended** approach for successful 200 responses as it's the most concise.

## Status Code Reference

### Common Status Codes

| Code | Meaning               | When to Use                                       |
| ---- | --------------------- | ------------------------------------------------- |
| 200  | OK                    | Successful GET, PUT, PATCH requests (default)     |
| 201  | Created               | Resource successfully created (POST)              |
| 204  | No Content            | Successful request with no response body (DELETE) |
| 400  | Bad Request           | Invalid request data or parameters                |
| 401  | Unauthorized          | Authentication required                           |
| 403  | Forbidden             | Access denied                                     |
| 404  | Not Found             | Resource not found (auto-handled)                 |
| 405  | Method Not Allowed    | HTTP method not allowed (auto-handled)            |
| 500  | Internal Server Error | Server error (auto-handled)                       |

### All Supported Status Codes

Wiverno supports all standard HTTP status codes:

**1xx Informational:**

- 100 Continue
- 101 Switching Protocols
- 102 Processing
- 103 Early Hints

**2xx Success:**

- 200 OK
- 201 Created
- 202 Accepted
- 203 Non-Authoritative Information
- 204 No Content
- 205 Reset Content
- 206 Partial Content
- 207 Multi-Status
- 208 Already Reported
- 226 IM Used

**3xx Redirection:**

- 300 Multiple Choices
- 301 Moved Permanently
- 302 Found
- 303 See Other
- 304 Not Modified
- 305 Use Proxy
- 307 Temporary Redirect
- 308 Permanent Redirect

**4xx Client Errors:**

- 400 Bad Request
- 401 Unauthorized
- 402 Payment Required
- 403 Forbidden
- 404 Not Found
- 405 Method Not Allowed
- 406 Not Acceptable
- 407 Proxy Authentication Required
- 408 Request Timeout
- 409 Conflict
- 410 Gone
- 411 Length Required
- 412 Precondition Failed
- 413 Content Too Large or Request Entity Too Larg
- 414 URI Too Long
- 415 Unsupported Media Type
- 416 Range Not Satisfiable
- 417 Expectation Failed
- 418 I'm a Teapot
- 421 Misdirected Request
- 422 Unprocessable Entity
- 423 Locked
- 424 Failed Dependency
- 425 Too Early
- 426 Upgrade Required
- 428 Precondition Required
- 429 Too Many Requests
- 431 Request Header Fields Too Large
- 451 Unavailable For Legal Reasons

**5xx Server Errors:**

- 500 Internal Server Error
- 501 Not Implemented
- 502 Bad Gateway
- 503 Service Unavailable
- 504 Gateway Timeout
- 505 HTTP Version Not Supported
- 506 Variant Also Negotiates
- 507 Insufficient Storage
- 508 Loop Detected
- 510 Not Extended
- 511 Network Authentication Required

## Best Practices

### 1. Use Integers for Non-200 Codes

**Recommended:**

```python
@app.post("/items")
def create_item(request):
    return 201, "Item created"
```

**Also valid, but more verbose:**

```python
@app.post("/items")
def create_item(request):
    return "201 Created", "Item created"
```

### 2. Omit Status for 200 OK

**Recommended:**

```python
@app.get("/items")
def list_items(request):
    return "<ul><li>Item 1</li></ul>"
```

**Unnecessary but valid:**

```python
@app.get("/items")
def list_items(request):
    return 200, "<ul><li>Item 1</li></ul>"
```

### 3. Be Consistent

Choose one style and stick with it throughout your application:

```python
# Good - Consistent style
@app.get("/users")
def list_users(request):
    return "Users list"

@app.post("/users")
def create_user(request):
    return 201, "User created"

@app.delete("/users/{id:int}")
def delete_user(request):
    return 204, ""
```

### 4. Use Appropriate Status Codes

```python
# Create resource - 201
@app.post("/posts")
def create_post(request):
    return 201, "Post created"

# Delete resource - 204
@app.delete("/posts/{id:int}")
def delete_post(request):
    return 204, ""

# Validation error - 400
@app.post("/users")
def create_user(request):
    if not request.data.get("email"):
        return 400, "Email required"
    return 201, "User created"

# Authentication required - 401
@app.get("/profile")
def profile(request):
    if not is_authenticated(request):
        return 401, "Authentication required"
    return "Profile data"

# Access denied - 403
@app.get("/admin")
def admin(request):
    if not is_admin(request):
        return 403, "Access denied"
    return "Admin panel"
```

## Error Handling

### Automatic Error Pages

Wiverno automatically handles these status codes:

- **404 Not Found** - When no route matches
- **405 Method Not Allowed** - When route exists but method isn't allowed
- **500 Internal Server Error** - When an unhandled exception occurs

```python
@app.get("/users")
def get_users(request):
    return "Users"

# GET /users -> 200 OK (handled)
# POST /users -> 405 Method Not Allowed (automatic)
# GET /nonexistent -> 404 Not Found (automatic)
```

### Custom Error Handlers

You can customize error pages by providing custom handlers:

```python
class Custom404:
    def __call__(self, request):
        return 404, "<h1>Page Not Found</h1>"

class Custom405:
    def __call__(self, request):
        return 405, f"<h1>Method {request.method} Not Allowed</h1>"

class Custom500:
    def __call__(self, request, error_traceback=None):
        return 500, "<h1>Server Error</h1>"

app = Wiverno(
    page_404=Custom404(),
    page_405=Custom405(),
    page_500=Custom500()
)
```

## Validation and Normalization

### How It Works

Wiverno uses the `HTTPStatusValidator` class to normalize all status codes:

```python
from wiverno.core.http.validator import HTTPStatusValidator

# All of these produce the same result: "201 Created"
HTTPStatusValidator.normalize_status(201)           # int
HTTPStatusValidator.normalize_status("201")         # string code
HTTPStatusValidator.normalize_status("201 Created") # full string
HTTPStatusValidator.normalize_status("201 Wrong")   # auto-corrected
```

### Invalid Status Codes

If you provide an invalid status code, Wiverno raises an exception:

```python
@app.get("/bad")
def bad_status(request):
    return 999, "Invalid"  # Raises ValueError: Unknown HTTP status code: 999

@app.get("/invalid")
def invalid_status(request):
    return "invalid", "Error"  # Raises InvalidHTTPStatusError
```

## Examples

### RESTful API

```python
from wiverno import Wiverno

app = Wiverno()

@app.get("/api/items")
def list_items(request):
    """List all items - 200 OK."""
    return '[{"id": 1, "name": "Item 1"}]'

@app.post("/api/items")
def create_item(request):
    """Create item - 201 Created."""
    return 201, '{"id": 2, "name": "New Item"}'

@app.get("/api/items/{id:int}")
def get_item(request):
    """Get item - 200 OK or 404."""
    item_id = request.path_params["id"]
    if item_id > 100:
        return 404, "Item not found"
    return f'{{"id": {item_id}, "name": "Item {item_id}"}}'

@app.put("/api/items/{id:int}")
def update_item(request):
    """Update item - 200 OK."""
    item_id = request.path_params["id"]
    return f'{{"id": {item_id}, "updated": true}}'

@app.delete("/api/items/{id:int}")
def delete_item(request):
    """Delete item - 204 No Content."""
    return 204, ""
```

### Form Validation

```python
@app.post("/register")
def register(request):
    """User registration with validation."""
    username = request.data.get("username", "").strip()
    email = request.data.get("email", "").strip()
    password = request.data.get("password", "")

    # Validation
    if not username:
        return 400, "Username is required"
    if len(username) < 3:
        return 400, "Username must be at least 3 characters"
    if not email or "@" not in email:
        return 400, "Valid email is required"
    if len(password) < 8:
        return 400, "Password must be at least 8 characters"

    # Success
    return 201, f"User {username} registered successfully"
```

### Authentication

```python
@app.post("/login")
def login(request):
    """User login."""
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return 400, "Username and password required"

    if not verify_credentials(username, password):
        return 401, "Invalid credentials"

    return "Login successful"

@app.get("/protected")
def protected(request):
    """Protected resource."""
    token = request.headers.get("Authorization")

    if not token:
        return 401, "Authentication required"

    if not verify_token(token):
        return 403, "Access denied"

    return "Protected data"
```

## See Also

- [Quickstart](quickstart.md) - Get started with Wiverno
- [Routing](routing.md) - Define routes and handlers
- [Requests](requests.md) - Handle incoming requests
- [Error Handling](routing.md#error-handling) - Custom error pages
