# Wiverno

**Wiverno** — a lightweight WSGI framework for building fast and flexible Python web applications.

## Installation

Clone the repository and install the package using `pip`:

```bash
pip install wiverno
```

## Minimal example

```python
from wiverno import Wiverno

app = Wiverno()

@app.get("/")
def index(request):
    return "200 OK", "<h1>Hello, World!</h1>"

@app.get("/users/{id:int}")
def get_user(request):
    user_id = request.path_params["id"]
    return "200 OK", f"<h1>User {user_id}</h1>"
```

## Running

Save the example above to `run.py` and start the development server:

```bash
wiverno run dev
```

The application will be available at `http://localhost:8000/`.


## Documentation

Full documentation is available at: **[https://sayrrexe.github.io/Wiverno/](https://sayrrexe.github.io/Wiverno/)**

The documentation includes:

- 📖 **User Guide** — getting started, routing, requests, and project structure
- 🔧 **API Reference** — complete API documentation for all modules
- 👨‍💻 **Developer Guide** — contributing guidelines, testing, and architecture overview

## Quick Links

- 📚 [Documentation](https://sayrrexe.github.io/Wiverno/)
- 🐛 [Issue Tracker](https://github.com/Sayrrexe/Wiverno/issues)
- 💬 [Discussions](https://github.com/Sayrrexe/Wiverno/discussions)
- 📋 [Changelog](https://github.com/Sayrrexe/Wiverno/releases)

## Requirements

- Python 3.12 or higher
- WSGI-compatible server (for production deployment)


## Contributing

Contributions are welcome! Please read the [Contributing Guide](https://sayrrexe.github.io/Wiverno/dev/contributing/) before submitting a pull request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

## Authors

- **Sayrrexe** — [GitHub](https://github.com/Sayrrexe)

