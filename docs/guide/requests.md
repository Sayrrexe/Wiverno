# Requests

Understanding request handling in Wiverno.

## Overview

The `Request` class provides access to all incoming HTTP request data including headers, query parameters, POST data, cookies, and more.

## Request Object

Every view function receives a `Request` object:

```python
from wiverno.core.requests import Request

def my_view(request: Request) -> tuple[str, str]:
    """View function with request parameter."""
    # Access request data here
    return "Response"
```

## Request Attributes

### HTTP Method

```python
def handle_request(request):
    """Check the HTTP method."""
    method = request.method  # "GET", "POST", "PUT", etc.

    if request.method == "GET":
        return "GET request"
    elif request.method == "POST":
        return 201, "POST request"
```

### Path Information

```python
def show_path(request):
    """Display request path."""
    path = request.path  # e.g., "/users/123"
    return f"<p>Path: {path}</p>"
```

### Path Parameters

Extract parameters from dynamic URL segments:

```python
@app.get("/users/{id:int}")
def get_user(request):
    """Get user by ID from path parameter."""
    user_id = request.path_params["id"]  # Already converted to int
    return f"<h1>User ID: {user_id}</h1>"

@app.get("/posts/{slug}/comments/{comment_id:int}")
def get_comment(request):
    """Get comment with multiple path parameters."""
    slug = request.path_params["slug"]           # str
    comment_id = request.path_params["comment_id"]  # int
    return f"<p>Post: {slug}, Comment: {comment_id}</p>"

@app.get("/files/{filepath:path}")
def serve_file(request):
    """Path parameter can contain slashes."""
    filepath = request.path_params["filepath"]  # e.g., "docs/guide/intro.md"
    return f"<p>File: {filepath}</p>"
```

**Supported types:**

- `{name}` or `{name:str}` - String (default)
- `{name:int}` - Integer (automatically converted)
- `{name:float}` - Float (automatically converted)
- `{name:path}` - Path (can contain slashes)

### Query Parameters

Parse query strings from GET requests using `QueryDict`:

```python
def search(request):
    """Handle search with query parameters."""
    # URL: /search?q=python&page=2&limit=10

    query = request.query_params.get("q", "")         # "python"
    page = request.query_params.get("page", "1")      # "2"
    limit = request.query_params.get("limit", "10")   # "10"

    return f"<p>Search: {query}, Page: {page}</p>"
```

**QueryDict** supports both single and multiple values:

```python
def search_with_tags(request):
    """Handle multiple query parameter values."""
    # URL: /search?q=python&tag=web&tag=framework&tag=wsgi

    # Get single value (first occurrence)
    query = request.query_params.get("q", "")  # "python"
    query = request.query_params["q"]          # Same, but raises KeyError if missing

    # Get all values for a parameter
    tags = request.query_params.getlist("tag")  # ["web", "framework", "wsgi"]

    # Get with default if not present
    categories = request.query_params.getlist("category", ["general"])  # ["general"]

    return f"<p>Query: {query}, Tags: {', '.join(tags)}</p>"
```

### POST Data

Access form data and JSON from POST requests:

```python
def handle_form(request):
    """Handle form submission."""
    if request.method == "POST":
        # Access POST data
        username = request.data.get("username", "")
        email = request.data.get("email", "")
        return f"User: {username}, Email: {email}"
    """
```

### JSON Data

Handle JSON POST requests:

```python
def api_create(request):
    """Handle JSON API request."""
    if request.method == "POST":
        # POST data is automatically parsed from JSON
        # Content-Type: application/json
        data = request.data

        name = data.get("name")
        age = data.get("age")

        return 201, f'{{"name": "{name}", "age": {age}}}'
```

### Headers

Access HTTP headers:

```python
def show_headers(request):
    """Display request headers."""
    headers = request.headers

    user_agent = headers.get("User-Agent", "Unknown")
    content_type = headers.get("Content-Type", "")
    accept = headers.get("Accept", "")

    return f"User-Agent: {user_agent}"

# Check for specific headers
def check_auth(request):
    """Check authorization header."""
    auth = request.headers.get("Authorization", "")
    if not auth:
        return 401, "Missing auth"
    return "Authorized"
```

### Cookies

Access request cookies:

```python
def show_cookies(request):
    """Display cookies."""
    cookies = request.cookies

    session_id = cookies.get("session_id", "")
    user_pref = cookies.get("preference", "default")

    return f"Session: {session_id}"
```

### Raw WSGI Environ

Access the raw WSGI environment:

```python
def debug_info(request):
    """Show raw WSGI environ."""
    environ = request.environ

    # Access any WSGI variable
    server_name = environ.get("SERVER_NAME")
    server_port = environ.get("SERVER_PORT")
    scheme = environ.get("wsgi.url_scheme")

    return f"Server: {server_name}:{server_port}"
```

## Request Body

### Reading Raw Body

Access raw request body:

```python
def handle_raw_body(request):
    """Read raw request body."""
    # Get content length
    content_length = int(request.environ.get("CONTENT_LENGTH", 0))

    if content_length > 0:
        # Read raw body
        wsgi_input = request.environ.get("wsgi.input")
        raw_body = wsgi_input.read(content_length)

        # Process raw bytes
        # raw_body is bytes

        return "Body processed"

    return 400, "No body"
```

### Multipart Form Data

Handle file uploads:

```python
def upload_file(request):
    """Handle file upload."""
    if request.method == "POST":
        # Multipart form data is parsed automatically
        # Content-Type: multipart/form-data

        file_content = request.data.get("file")
        filename = request.data.get("filename", "upload.txt")

        # Save file or process content
        # file_content is the file data

        return f"Uploaded: {filename}"

    return """
        <form method="post" enctype="multipart/form-data">
            <input type="file" name="file">
            <button type="submit">Upload</button>
        </form>
    """
```

## Content Types

Wiverno automatically handles different content types:

### application/x-www-form-urlencoded

Standard HTML form submission:

```python
def handle_form(request):
    """Handle URL-encoded form."""
    # Content-Type: application/x-www-form-urlencoded
    username = request.data.get("username")
    password = request.data.get("password")
    return "Form received"
```

### application/json

JSON API requests:

```python
def api_endpoint(request):
    """Handle JSON request."""
    # Content-Type: application/json
    data = request.data
    # data is already a dict
    return "JSON received"
```

### multipart/form-data

File uploads and mixed data:

```python
def upload(request):
    """Handle multipart form."""
    # Content-Type: multipart/form-data; boundary=...
    file_data = request.data.get("file")
    description = request.data.get("description")
    return "Upload received"
```

## Request Parsing Utilities

Wiverno provides utility classes for parsing:

### QueryDict

The `QueryDict` class handles query parameters with support for multiple values:

```python
from wiverno.core.requests import QueryDict

# Parse query string
query_dict = QueryDict("name=John&age=30&tag=python&tag=web")

# Get single values
name = query_dict.get("name")  # "John"
age = query_dict["age"]        # "30"

# Get multiple values
tags = query_dict.getlist("tag")  # ["python", "web"]

# Iteration (returns first value for each key)
for key in query_dict:
    print(f"{key}: {query_dict[key]}")
```

### ParseBody

```python
from wiverno.core.requests import ParseBody

# Parse POST body
raw_data = b'{"name": "John"}'
params = ParseBody.get_request_params(environ, raw_data)
```

### HeaderParser

```python
from wiverno.core.requests import HeaderParser

# Parse headers
headers = HeaderParser.get_headers(environ)
```

## Common Patterns

### Check Request Method

```python
def resource(request):
    """Handle different HTTP methods."""
    if request.method == "GET":
        return "Get resource"
    elif request.method == "POST":
        return 201, "Created resource"
    elif request.method == "PUT":
        return "Updated resource"
    elif request.method == "DELETE":
        return 204, ""
    else:
        return 405, ""
```

### Validate Input

```python
def create_user(request):
    """Create user with validation."""
    if request.method != "POST":
        return 405, ""

    # Get data
    username = request.data.get("username", "").strip()
    email = request.data.get("email", "").strip()

    # Validate
    if not username:
        return 400, "Username required"
    if not email:
        return 400, "Email required"
    if "@" not in email:
        return 400, "Invalid email"

    # Process
    return 201, f"User {username} created"
```

### Parse Pagination

```python
def list_items(request):
    """List items with pagination."""
    # Get page and limit from query
    page = int(request.query_params.get("page", "1"))
    limit = int(request.query_params.get("limit", "10"))

    # Validate
    if page < 1:
        page = 1
    if limit < 1 or limit > 100:
        limit = 10

    # Calculate offset
    offset = (page - 1) * limit

    return f"Page {page}, Limit {limit}, Offset {offset}"
```

### Handle API Authentication

```python
def protected_endpoint(request):
    """Require API key."""
    api_key = request.headers.get("X-API-Key", "")

    if not api_key:
        return 401, '{"error": "API key required"}'

    if api_key != "secret-key":
        return 403, '{"error": "Invalid API key"}'

    # Authorized
    return '{"data": "protected data"}'
```

## Best Practices

### 1. Always Validate Input

```python
def safe_handler(request):
    """Validate all input."""
    value = request.query_params.get("value", "")

    # Validate
    if not value:
        return 400, "Value required"

    # Sanitize
    value = value.strip()[:100]  # Limit length

    return f"Value: {value}"
```

### 2. Use Type Conversion Safely

```python
def get_page(request):
    """Safe type conversion."""
    try:
        page = int(request.query_params.get("page", "1"))
    except ValueError:
        page = 1

    # Ensure valid range
    page = max(1, min(page, 1000))

    return f"Page {page}"
```

### 3. Handle Missing Data

```python
def safe_access(request):
    """Use .get() with defaults."""
    # Good
    name = request.query_params.get("name", "Guest")

    # Bad - may raise KeyError
    # name = request.query_params["name"]
```

## Next Steps

- [Routing](routing.md) - Define routes and handlers
- [HTTP Status Codes](status-codes.md) - Understanding status codes
- [Class-Based Views](../api/views/base-views.md) - Organize with class-based views
- [Templates](../api/templating/templator.md) - Render HTML templates
