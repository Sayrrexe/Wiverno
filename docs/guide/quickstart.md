# Quickstart

This guide will help you create your first Wiverno application in just a few minutes.

## Prerequisites

Make sure you have [installed Wiverno](installation.md) before continuing.

## Your First Application

Let's create a simple "Hello, World!" application.

### Step 1: Create a Python File

Create a new file called `app.py`:

```python
from wiverno.main import Wiverno

app = Wiverno()

@app.get("/")
def index(request):
    """Homepage view function."""
    return "200 OK", "Hello, World!"
```

### Step 2: Run the Application

Use the Wiverno CLI to start the development server:

```bash
wiverno run dev app:app
```

You should see output like:

```
Starting development server on http://localhost:8000
Press Ctrl+C to stop
```

### Step 3: Visit the Application

Open your browser and go to [http://localhost:8000](http://localhost:8000). You should see "Hello, World!".

Congratulations! 🎉 You've created your first Wiverno application!

## Adding More Routes

Let's expand the application with more routes using decorators:

```python
from wiverno.main import Wiverno

app = Wiverno()

@app.get("/")
def index(request):
    """Homepage view."""
    return "200 OK", "Hello, World!"

@app.get("/about")
def about(request):
    """About page view."""
    return "200 OK", "This is the about page"

```

Run with:

```bash
wiverno run dev app:app
```

Now you can visit:

- [http://localhost:8000/](http://localhost:8000/) - Homepage
- [http://localhost:8000/about](http://localhost:8000/about) - About page

## Handling Different HTTP Methods

You can handle different HTTP methods using method-specific decorators:

```python
from wiverno.main import Wiverno

app = Wiverno()

@app.get("/users")
def get_users(request):
    """Handle GET requests - list users."""
    return "200 OK", "Get user list"

@app.post("/users")
def create_user(request):
    """Handle POST requests - create user."""
    return "201 CREATED", "User created"
```

Or use class-based views for better organization:

```python
from wiverno.views.base_views import BaseView

class UserView(BaseView):
    """Handle user-related requests."""

    def get(self, request):
        return "200 OK", "Get user info"

    def post(self, request):
        return "201 CREATED", "User created"

    def put(self, request):
        return "200 OK", "User updated"

    def delete(self, request):
        return "204 NO CONTENT", ""

app = Wiverno(routes_list=[
    ("/users", UserView()),
])
```

## Using Templates

Wiverno comes with built-in Jinja2 template support:

### Step 1: Create a Template

Create a `templates` directory and add `index.html`:

```html
<!DOCTYPE html>
<html>
  <head>
    <title>{{ title }}</title>
  </head>
  <body>
    <h1>{{ heading }}</h1>
    <p>{{ message }}</p>
  </body>
</html>
```

### Step 2: Render the Template

```python
from wiverno.main import Wiverno
from wiverno.templating.templator import Templator

# Initialize template renderer
templator = Templator(folder="templates")

@app.get("/")
def index(request):
    """Homepage with template."""
    html = templator.render("index.html", content={
        "title": "Welcome",
        "heading": "Hello, Wiverno!",
        "message": "This is a template-rendered page."
    })
    return "200 OK", html

app = Wiverno()
```

## Working with Request Data

### Query Parameters

```python
@app.get("/search")
def search(request):
    """Search page with query parameters."""
    query = request.query_params.get("q", "")
    return "200 OK", f"Searching for: {query}"
```

Visit: [http://localhost:8000/search?q=python](http://localhost:8000/search?q=python)

### POST Data

```python
@app.route("/submit", methods=["GET", "POST"])
def submit(request):
    """Handle form submission."""
    if request.method == "POST":
        # Access POST data
        name = request.data.get("name", "")
        email = request.data.get("email", "")
        return "200 OK", f"Received: {name} ({email})"
    return "200 OK", "Send a POST request"
```

### Headers

```python
@app.get("/headers")
def headers_info(request):
    """Display request headers."""
    user_agent = request.headers.get("User-Agent", "Unknown")
    return "200 OK", f"Your user agent: {user_agent}"
```

## Development Mode with Auto-Reload

**Always use the Wiverno CLI for development** - it provides auto-reload:

```bash
wiverno run dev --app-module app --app-name app
```

Or with default module name:

```bash
wiverno run dev
```

The server will automatically reload when you make changes to your code. This is the recommended way to run your application during development.

## Configuration

You can configure the server with custom host and port using CLI options:

```bash
# Custom host and port
wiverno run dev --host 0.0.0.0 --port 5000 --app-module myapp --app-name application
```

For production, use a production WSGI server like gunicorn or waitress (see deployment docs).

## Next Steps

Now that you've created your first Wiverno application, explore these topics:

- [**Routing**](routing.md) - Learn more about URL routing
- [**Requests**](requests.md) - Deep dive into request handling

Happy coding!
