# Wiverno

**Wiverno** — a lightweight WSGI framework for building fast and flexible Python web applications.

## Installation

Clone the repository and install the package using `pip`:

```bash
pip install .
```

## Minimal example

```python
from wiverno.main import Wiverno

app = Wiverno()

@app.get("/")
def index(request):
    return "200 OK", "Hello, World!"
```

## Running

Save the example above to `run.py` and start the development server:

```bash
wiverno run dev
```

The application will be available at `http://localhost:8000/`.
