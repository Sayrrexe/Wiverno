# Project Structure

Learn how to organize your Wiverno application for maintainability and scalability.

## Minimal Structure

For small applications, a simple single-file structure works well:

```
myapp/
├── run.py
└── templates/
    └── index.html
```

## Recommended Structure

For production applications, we recommend the following structure:

```
myproject/
├── run.py              # Application entry point
├── requirements.txt    # Dependencies
├── config.py          # Configuration
├── .env               # Environment variables
├── templates/         # Jinja2 templates
│   ├── base.html
│   ├── index.html
│   └── ...
├── static/            # Static files
│   ├── css/
│   ├── js/
│   └── images/
├── views/             # View functions/classes
│   ├── __init__.py
│   ├── home.py
│   ├── api.py
│   └── ...
├── models/            # Data models (if using a database)
│   ├── __init__.py
│   └── user.py
├── middleware/        # Custom middleware
│   ├── __init__.py
│   └── auth.py
└── tests/             # Tests
    ├── __init__.py
    ├── test_views.py
    └── ...
```

## File-by-File Breakdown

### run.py

The main entry point of your application:

```python
"""Main application module."""
from wiverno.main import Wiverno
from views.home import home_router
from views.api import api_router

app = Wiverno()

# Include routers with prefixes
app.include_router(home_router, prefix="")
app.include_router(api_router, prefix="/api")
```

Run with:

```bash
wiverno run dev
```

### config.py

Application configuration:

```python
"""Application configuration."""
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent
TEMPLATE_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

# Server configuration
HOST = os.getenv("HOST", "localhost")
PORT = int(os.getenv("PORT", 8000))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Application settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
```

### views/home.py

View functions organized by feature using Router:

```python
"""Home page views."""
from wiverno.core.routing.router import Router
from wiverno.templating.templator import Templator

home_router = Router()
templator = Templator()

@home_router.get("/")
def index(request):
    """Homepage."""
    html = templator.render("index.html", {
        "title": "Home"
    })
    return html

@home_router.get("/about")
def about(request):
    """About page."""
    html = templator.render("about.html", {
        "title": "About"
    })
    return html
```

### views/api.py

API endpoints using Router:

```python
"""API views."""
import json
from wiverno.core.routing.router import Router

api_router = Router()

@api_router.get("/users")
def api_users(request):
    """Get all users."""
    users = [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},
    ]
    return json.dumps(users)

@api_router.get("/users/<id>")
def api_user_detail(request):
    """Get user by ID."""
    user_id = request.path_params.get("id")
    user = {"id": user_id, "name": "User"}
    return json.dumps(user)
```

## Scaling Your Application

### Blueprint Pattern

For larger applications, organize views into blueprints using Router:

````python
# views/blog/__init__.py
"""Blog blueprint."""
from wiverno.core.routing.router import Router

blog_router = Router()

@blog_router.get("/")
def list_posts(request):
    """List all blog posts."""
    return "Blog posts"

@blog_router.get("/<slug>")
def post_detail(request):
    """Get single blog post."""
    slug = request.path_params.get("slug")
    return f"Blog post {slug}"

# In app.py
from wiverno.main import Wiverno
from views.blog import blog_router

app = Wiverno()
app.include_router(blog_router, prefix="/blog")
```### Middleware Organization

```python
# middleware/auth.py
"""Authentication middleware."""

class AuthMiddleware:
    """Check authentication for protected routes."""

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        path = environ.get("PATH_INFO", "")

        # Check if path requires authentication
        if path.startswith("/admin"):
            # Verify authentication
            token = environ.get("HTTP_AUTHORIZATION")
            if not token:
                start_response("401 Unauthorized", [])
                return [b"Unauthorized"]

        return self.app(environ, start_response)
````

## Environment Variables

Use `.env` file for sensitive configuration:

```env
# .env
DEBUG=true
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///db.sqlite3
HOST=0.0.0.0
PORT=8000
```

Load in your application:

```python
# run.py
from dotenv import load_dotenv
load_dotenv()
```

## Testing Structure

Organize tests to mirror your application structure:

```
tests/
├── __init__.py
├── conftest.py         # Pytest fixtures
├── test_app.py         # Application tests
├── views/
│   ├── test_home.py
│   └── test_api.py
└── integration/
    └── test_full_flow.py
```

## Next Steps

- [**Routing**](routing.md) - Learn about advanced routing patterns
- [**Class-Based Views**](../api/views/base-views.md) - Master view organization
- [**Templates**](../api/templating/templator.md) - Template best practices
