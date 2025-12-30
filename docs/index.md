# Welcome to Wiverno

**Wiverno** is a lightweight WSGI framework for building fast and flexible Python web applications.

## Why Wiverno?

- **🚀 Fast**: Built on WSGI with minimal overhead
- **🎯 Simple**: Clean and intuitive API
- **📦 Lightweight**: Minimal dependencies, maximum performance
- **🔧 Flexible**: Easy to extend and customize
- **🐍 Modern Python**: Built for Python 3.12+

## Features

- **Simple routing system** - Define routes with decorators
- **Request/Response handling** - Clean abstractions for HTTP requests
- **Template engine integration** - Built-in Jinja2 support via Templator
- **Class-based views** - BaseView for better code organization
- **Development server** - Hot-reload during development
- **CLI tools** - Command-line interface for common tasks

## Quick Example

```python
from wiverno.main import Wiverno

app = Wiverno()

@app.get("/")
def index(request):
    return "Hello, World!"
```

Save this as `run.py` and run:

```bash
wiverno run dev
```

Visit [http://localhost:8000](http://localhost:8000) to see your app in action!

## Getting Started

<div class="grid cards" markdown>

- :material-clock-fast:{ .lg .middle } **Quick Start**

  ***

  Get up and running in minutes with our quick start guide.

  [:octicons-arrow-right-24: Quickstart](guide/quickstart.md)

- :material-book-open-page-variant:{ .lg .middle } **User Guide**

  ***

  Learn the core concepts and features of Wiverno.

  [:octicons-arrow-right-24: Read the Guide](guide/index.md)

- :material-code-braces:{ .lg .middle } **API Reference**

  ***

  Detailed documentation of all classes and functions.

  [:octicons-arrow-right-24: API Docs](api/index.md)

- :material-hand-heart:{ .lg .middle } **Contributing**

  ***

  Want to contribute? Check out our development guide.

  [:octicons-arrow-right-24: Development](dev/index.md)

</div>

## Installation

Install Wiverno using pip:

```bash
pip install wiverno
```

Or install from source:

```bash
git clone https://github.com/Sayrrexe/Wiverno.git
cd Wiverno
pip install .
```

For development:

```bash
pip install -e ".[dev]"
```

## Community

- **GitHub**: [github.com/Sayrrexe/Wiverno](https://github.com/Sayrrexe/Wiverno)
- **Issues**: [Report bugs or request features](https://github.com/Sayrrexe/Wiverno/issues)
- **Pull Requests**: [Contributions welcome!](https://github.com/Sayrrexe/Wiverno/pulls)

## License

Wiverno is licensed under the [MIT License](https://github.com/Sayrrexe/Wiverno/blob/main/LICENSE).
