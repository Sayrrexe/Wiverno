# User Guide

Welcome to the Wiverno User Guide! This guide will help you understand and use all the features of the Wiverno framework.

## Table of Contents

### Getting Started

Start here if you're new to Wiverno:

- [**Installation**](installation.md) - How to install Wiverno
- [**Quickstart**](quickstart.md) - Your first Wiverno application
- [**Project Structure**](project-structure.md) - How to organize your Wiverno project

### Core Concepts

Learn the fundamental concepts of Wiverno:

- [**Routing**](routing.md) - Define URL patterns and handlers
- [**Requests**](requests.md) - Handle incoming HTTP requests
- [**HTTP Status Codes**](status-codes.md) - Working with HTTP status codes

### Advanced Topics

Take your Wiverno skills to the next level:

- [**Class-Based Views**](../api/views/base-views.md) - Organize your code with class-based views
- [**Templates**](../api/templating/templator.md) - Render HTML with Jinja2
- [**CLI**](../guide/cli.md) - Use the command-line interface

## Philosophy

Wiverno is designed with the following principles in mind:

### Simplicity First

Wiverno aims to be easy to learn and use. The API is intentionally small and focused on the essentials.

```python
# Simple routing
app = Wiverno()

@app.get("/")
def index(request):
    return "Hello, World!"

@app.get("/about")
def about(request):
    return "About"
```

### Explicit Over Implicit

Wiverno prefers explicit configuration over magic. You always know what's happening:

```python
# Explicit status codes and content
def view(request):
    return "Hello, World!"
```

### Flexibility

Wiverno doesn't force you into a specific way of doing things. Use what you need, ignore what you don't:

```python
# Function-based views
def simple_view(request):
    return "Simple"

# Or class-based views
class ComplexView(BaseView):
    def get(self, request):
        return "Complex"
```

## Next Steps

Ready to get started? Head over to the [Installation](installation.md) guide to set up Wiverno, or jump straight to the [Quickstart](quickstart.md) to build your first application!
