# Templator

The `Templator` class provides a simple wrapper around Jinja2 for rendering templates in Wiverno applications.

## Module: `wiverno.templating.templator`

## Overview

`Templator` simplifies template rendering by:

- Loading templates from a specified directory
- Providing a clean `render()` method
- Handling template inheritance and includes
- Supporting all Jinja2 features (filters, macros, etc.)

## Constructor

### `Templator(folder="templates")`

Creates a new templator instance with a template directory.

**Parameters:**

- `folder` (str | Path, optional): Path to templates folder. Can be absolute or relative to current working directory. Defaults to `"templates"`

**Returns:** `Templator` instance

```python
from wiverno.templating.templator import Templator

# Relative path (relative to current working directory)
templator = Templator(folder="templates")

# Absolute path
templator = Templator(folder="/absolute/path/to/templates")

# Using Path object
from pathlib import Path
templator = Templator(folder=Path("my_templates"))
```

## Methods

### `render(template_name, content=None, **kwargs) -> str`

Renders a template with the given context.

**Parameters:**

- `template_name` (str): Name of the template file to render
- `content` (dict, optional): Context dictionary with template variables. Defaults to `None` (empty dict)
- `**kwargs`: Additional context variables as keyword arguments

**Returns:** `str` - Rendered HTML as a string

**Raises:**

- `TypeError` - If `content` is not a dictionary or `None`
- `jinja2.TemplateNotFound` - If template file doesn't exist
- `jinja2.TemplateSyntaxError` - If template has syntax errors

```python
from wiverno.templating.templator import Templator

templator = Templator()

# Render with content dict
html = templator.render("index.html", {"title": "Home"})

# Render with keyword arguments
html = templator.render("page.html", title="About", author="John")

# Render with both
html = templator.render(
    "post.html",
    {"title": "My Post"},
    author="Jane",
    date="2024-01-01"
)
```

## Attributes

### `env: Environment`

The Jinja2 `Environment` instance used for template rendering. Access this for advanced Jinja2 features.

```python
templator = Templator()

# Add custom Jinja2 filter
@templator.env.filter('multiply')
def multiply(value, num):
    return value * num
```

### `base_dir: Path`

The base directory for relative template paths. Defaults to current working directory.

```python
templator = Templator()
print(templator.base_dir)  # Path object of current directory
```

## Usage Examples

### Basic Template Rendering

Create a template file `templates/index.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
</head>
<body>
    <h1>{{ title }}</h1>
</body>
</html>
```

Render it in your view:

```python
from wiverno.main import Wiverno
from wiverno.templating.templator import Templator

app = Wiverno()
templator = Templator()

@app.get("/")
def home(request):
    html = templator.render("index.html", {"title": "Welcome"})
    return "200 OK", html
```

### Multiple Context Variables

Template `templates/post.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
</head>
<body>
    <h1>{{ title }}</h1>
    <p>By {{ author }}</p>
    <p>{{ content }}</p>
</body>
</html>
```

Render with multiple variables:

```python
@app.get("/blog/post")
def blog_post(request):
    html = templator.render("post.html", {
        "title": "My First Post",
        "author": "Jane Doe",
        "content": "Lorem ipsum..."
    })
    return "200 OK", html
```

### Using Keyword Arguments

```python
@app.get("/profile")
def profile(request):
    html = templator.render(
        "profile.html",
        username="john_doe",
        email="john@example.com",
        bio="Web developer"
    )
    return "200 OK", html
```

### Template Inheritance

Base template `templates/base.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}My Site{% endblock %}</title>
</head>
<body>
    <nav>Navigation</nav>
    {% block content %}{% endblock %}
</body>
</html>
```

Child template `templates/page.html`:

```html
{% extends "base.html" %}

{% block title %}{{ page_title }}{% endblock %}

{% block content %}
    <h1>{{ page_title }}</h1>
    <p>{{ text }}</p>
{% endblock %}
```

Render:

```python
@app.get("/page")
def page(request):
    html = templator.render("page.html", {
        "page_title": "About Us",
        "text": "Welcome to our site!"
    })
    return "200 OK", html
```

### Template Includes

Main template `templates/layout.html`:

```html
<!DOCTYPE html>
<html>
<head>
    {% include "head.html" %}
</head>
<body>
    {% include "header.html" %}
    <main>
        {% block content %}{% endblock %}
    </main>
    {% include "footer.html" %}
</body>
</html>
```

Render:

```python
@app.get("/")
def index(request):
    html = templator.render("layout.html", {
        "page_title": "Home"
    })
    return "200 OK", html
```

### Custom Jinja2 Filters

```python
from wiverno.templating.templator import Templator

templator = Templator()

# Add custom filter
@templator.env.filter('uppercase')
def uppercase(value):
    return value.upper()

# In template: {{ text | uppercase }}
```

### List and Dict Context

Template `templates/users.html`:

```html
<ul>
{% for user in users %}
    <li>{{ user.name }} - {{ user.email }}</li>
{% endfor %}
</ul>
```

Render:

```python
@app.get("/users")
def list_users(request):
    users_data = [
        {"name": "Alice", "email": "alice@example.com"},
        {"name": "Bob", "email": "bob@example.com"},
    ]
    html = templator.render("users.html", {"users": users_data})
    return "200 OK", html
```

### Conditional Content

Template `templates/dashboard.html`:

```html
{% if user_is_admin %}
    <a href="/admin">Admin Panel</a>
{% else %}
    <p>You don't have admin access</p>
{% endif %}
```

Render:

```python
@app.get("/dashboard")
def dashboard(request):
    is_admin = request.query_params.get('admin') == 'true'
    html = templator.render("dashboard.html", {
        "user_is_admin": is_admin
    })
    return "200 OK", html
```

## Jinja2 Features

All standard Jinja2 features are available:

### Filters

```html
{{ text | lower }}
{{ price | round(2) }}
{{ items | length }}
{{ text | replace('old', 'new') }}
```

### Loops and Conditionals

```html
{% for item in items %}
    {% if item.active %}
        <p>{{ item.name }}</p>
    {% endif %}
{% endfor %}
```

### Macros

```html
{% macro render_item(item) %}
    <div class="item">{{ item.name }}</div>
{% endmacro %}

{{ render_item(my_item) }}
```

### Template Comments

```html
{# This is a comment and won't be rendered #}
```

## Auto-Escaping

By default, `Templator` enables auto-escaping to prevent HTML injection vulnerabilities:

```python
# Template variable is auto-escaped
{{ user_input | safe }}  # Use |safe filter to disable escaping if needed
```

## Error Handling

```python
from wiverno.templating.templator import Templator
import jinja2

templator = Templator()

try:
    html = templator.render("nonexistent.html")
except jinja2.TemplateNotFound:
    print("Template not found")
except TypeError:
    print("Context must be a dictionary")
```

## Path Resolution

Template paths are resolved as follows:

1. If `folder` is absolute, use it directly
2. If `folder` is relative, resolve relative to current working directory

```python
# Current working directory: /home/user/myapp

# Relative path
templator = Templator("templates")
# Resolves to: /home/user/myapp/templates

# Absolute path
templator = Templator("/etc/templates")
# Resolves to: /etc/templates
```

## See Also

- [Application](../core/application.md) - Wiverno application class
- [Request](../core/requests.md) - Request handling
- [Jinja2 Documentation](https://jinja.palletsprojects.com/) - Official Jinja2 docs
