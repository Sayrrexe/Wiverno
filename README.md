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
