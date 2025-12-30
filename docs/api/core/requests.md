# Request Handling

The `Request` class represents an HTTP request parsed from the WSGI environment. It provides convenient access to all request data.

## Module: `wiverno.core.requests`

## Request Class

```python
from wiverno.core.requests import Request

def my_view(request: Request) -> tuple[str, str]:
    # Access request properties
    method = request.method  # 'GET', 'POST', etc.
    path = request.path     # '/users'
    return "Hello"
```

## Properties

All properties are read-only and populated from the WSGI environment.

### HTTP Method and Path

#### `method: str`

The HTTP method of the request.

- Examples: `"GET"`, `"POST"`, `"PUT"`, `"DELETE"`, `"PATCH"`

```python
if request.method == "GET":
    return "Retrieved"
elif request.method == "POST":
    return 201, "Created"
```

#### `path: str`

The normalized URL path of the request. Trailing slashes are removed except for the root path `"/"`.

- `/users` (trailing slash removed)
- `/users/` becomes `/users`
- `/` stays `/`

```python
if request.path == "/":
    return "Home"
elif request.path == "/about":
    return "About"
```

### Request Data

#### `query_params: dict[str, Any]`

Parsed query string parameters from the URL. Only the first value is returned for each parameter.

```python
# URL: /search?q=python&category=web

print(request.query_params)
# Output: {'q': 'python', 'category': 'web'}

search_term = request.query_params.get('q')
```

#### `data: dict[str, Any]`

Parsed request body. Content parsing is automatic based on `Content-Type` header:

- `application/json` - JSON decoded
- `application/x-www-form-urlencoded` - Form data
- `multipart/form-data` - File uploads and form fields
- Other content types return empty dict

```python
@app.post("/users")
def create_user(request):
    # For JSON POST: {"name": "John", "email": "john@example.com"}
    name = request.data.get('name')
    email = request.data.get('email')
    return 201, f"Created user {name}"
```

### Headers and Cookies

#### `headers: dict[str, str]`

All HTTP request headers as a dictionary. Header names are normalized (e.g., "Content-Type").

```python
content_type = request.headers.get('Content-Type')
user_agent = request.headers.get('User-Agent')
```

#### `cookies: dict[str, str]`

Parsed cookies from the `Cookie` header.

```python
session_id = request.cookies.get('session_id')
user_pref = request.cookies.get('user_preference')
```

#### `content_type: str`

The value of the `Content-Type` header.

```python
if "application/json" in request.content_type:
    # Handle JSON data
    pass
```

#### `content_length: int`

The size of the request body in bytes. Returns 0 if `Content-Length` header is missing or invalid.

```python
if request.content_length > 10_000_000:
    return "413 PAYLOAD TOO LARGE", "Request too large"
```

### Connection Information

#### `client_ip: str`

The IP address of the client making the request.

```python
print(f"Request from: {request.client_ip}")
```

#### `server: str`

The hostname or IP address of the server.

```python
print(f"Server name: {request.server}")
```

#### `user_agent: str`

The `User-Agent` header value.

```python
if "Mobile" in request.user_agent:
    # Serve mobile-optimized content
    pass
```

#### `protocol: str`

The HTTP protocol version (e.g., `"HTTP/1.1"`, `"HTTP/2.0"`).

```python
print(f"Protocol: {request.protocol}")
```

#### `scheme: str`

The URL scheme of the request. Either `"http"` or `"https"`.

```python
print(f"Scheme: {request.scheme}")
```

#### `is_secure: bool`

Whether the connection is secure (HTTPS). Equivalent to `request.scheme == "https"`.

```python
if request.is_secure:
    # HTTPS connection
    pass
else:
    # HTTP connection
    pass
```

### WSGI Environment

#### `environ: dict`

The raw WSGI environment dictionary. Use this for advanced use cases.

```python
# Access raw WSGI environ if needed
remote_port = request.environ.get('REMOTE_PORT')
```

## Helper Classes

### ParseQuery

Utility class for parsing URL query strings.

```python
from wiverno.core.requests import ParseQuery

# Parse query string
query_dict = ParseQuery.parse_input_data("name=John&age=30")
# Output: {'name': 'John', 'age': '30'}

# Get query params from WSGI environ
params = ParseQuery.get_request_params(environ)
```

### ParseBody

Handles parsing of POST request bodies with support for multiple content types.

```python
from wiverno.core.requests import ParseBody

# Parse request body
data = ParseBody.get_request_params(environ, raw_bytes)
```

Supported content types:

- `multipart/form-data` - File uploads and form data
- `application/x-www-form-urlencoded` - Form submissions
- `application/json` - JSON data

### HeaderParser

Utility class for parsing HTTP headers from WSGI environment.

```python
from wiverno.core.requests import HeaderParser

# Get all headers
headers = HeaderParser.get_headers(environ)
```

## Examples

### Simple GET Request

```python
@app.get("/")
def home(request: Request) -> tuple[str, str]:
    return "<html><body>Home</body></html>"
```

### GET with Query Parameters

```python
@app.get("/search")
def search(request: Request) -> tuple[str, str]:
    q = request.query_params.get('q', '')
    return f"<html><body>Search results for: {q}</body></html>"
```

### POST with JSON Data

```python
@app.post("/api/users")
def create_user(request: Request) -> tuple[str, str]:
    data = request.data
    name = data.get('name')
    email = data.get('email')

    if not name or not email:
        return 400, "Missing required fields"

    return 201, f"User {name} created"
```

### POST with Form Data

```python
@app.post("/login")
def login(request: Request) -> tuple[str, str]:
    username = request.data.get('username')
    password = request.data.get('password')

    if username == "admin" and password == "secret":
        return "200 OK", "Login successful"
    else:
        return "401 UNAUTHORIZED", "Invalid credentials"
```

### Checking Headers

```python
@app.post("/api/data")
def api_endpoint(request: Request) -> tuple[str, str]:
    auth_header = request.headers.get('Authorization')

    if not auth_header:
        return "401 UNAUTHORIZED", "Missing Authorization header"

    if not auth_header.startswith('Bearer '):
        return "401 UNAUTHORIZED", "Invalid token format"

    token = auth_header[7:]  # Remove 'Bearer ' prefix
    return "200 OK", "Authorized"
```

### Using Cookies

```python
@app.get("/profile")
def profile(request: Request) -> tuple[str, str]:
    session_id = request.cookies.get('session_id')

    if not session_id:
        return "401 UNAUTHORIZED", "No session"

    # Validate session_id
    return "200 OK", f"<html><body>Profile</body></html>"
```

## See Also

- [Application](application.md) - Main Wiverno application class
- [Router](router.md) - URL routing
- [Base Views](../views/base-views.md) - Class-based views
