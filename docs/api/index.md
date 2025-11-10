# API Reference

Welcome to the Wiverno API Reference documentation. This section provides detailed information about all classes, functions, and modules in the Wiverno framework.

## Overview

The Wiverno API is organized into several key modules:

### Core Modules

These are the fundamental building blocks of Wiverno:

- [**Application**](core/application.md) - The main Wiverno WSGI application class
- [**Requests**](core/requests.md) - HTTP request parsing and handling
- [**Router**](core/router.md) - Modular routing and URL path matching
- [**Server**](core/server.md) - WSGI server wrapper for development and testing

### Templating

Template rendering functionality:

- [**Templator**](templating/templator.md) - Jinja2 template rendering wrapper

### Views

View classes for organizing your code:

- [**Base Views**](views/base-views.md) - Class-based view foundation with HTTP method dispatch

### CLI

Command-line interface tools:

- [**CLI**](cli.md) - Command-line commands for running servers and documentation

## Quick Reference

### Common Imports

```python
# Main application
from wiverno.main import Wiverno

# Server
from wiverno.core.server import RunServer

# Request handling
from wiverno.core.requests import Request

# Routing
from wiverno.core.router import Router

# Templates
from wiverno.templating.templator import Templator

# Views
from wiverno.views.base_views import BaseView

# Development server
from wiverno.dev.dev_server import DevServer
```

## API Stability

Wiverno follows [Semantic Versioning](https://semver.org/):

- **Major version** (X.0.0) - Breaking API changes
- **Minor version** (0.X.0) - New features, backward compatible
- **Patch version** (0.0.X) - Bug fixes, backward compatible

### Stability Indicators

- ✅ **Stable** - Safe to use in production
- ⚠️ **Beta** - API may change in minor versions
- 🚧 **Experimental** - API may change at any time

## Type Hints

Wiverno uses Python type hints throughout the codebase. All public APIs have complete type annotations for better IDE support and type checking.

```python
from wiverno.main import Wiverno
from wiverno.core.requests import Request

def my_view(request: Request) -> tuple[str, str]:
    """Type-annotated view function."""
    return "200 OK", "Hello!"

app: Wiverno = Wiverno(routes_list=[
    ("/", my_view),
])
```

## Documentation Conventions

### Function Signatures

```python
def function_name(
    param1: Type1,
    param2: Type2 = default_value,
    *args: Type3,
    **kwargs: Type4
) -> ReturnType:
    """Brief description.

    Detailed description of what the function does.

    Args:
        param1: Description of param1
        param2: Description of param2
        *args: Description of args
        **kwargs: Description of kwargs

    Returns:
        Description of return value

    Raises:
        ExceptionType: When this exception is raised

    Example:
        >>> function_name(value1, value2)
        result
    """
```

### Class Documentation

```python
class ClassName:
    """Brief description.

    Detailed description of what the class does.

    Attributes:
        attr1: Description of attr1
        attr2: Description of attr2

    Example:
        >>> obj = ClassName()
        >>> obj.method()
        result
    """
```

## Next Steps

Browse the detailed API documentation for each module:

- Start with [**Application**](core/application.md) to understand the main Wiverno class
- Learn about [**Request Handling**](core/requests.md) to work with HTTP requests
- Explore [**Routing**](core/router.md) for URL pattern matching
- Check out [**Base Views**](views/base-views.md) for class-based views
