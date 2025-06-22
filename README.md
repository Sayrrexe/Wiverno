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
from wiverno.core.server import RunServer

def index(request):
    return "200 OK", "Hello, World!"

app = Wiverno(routes_list=[("/", index)])
RunServer(app).start()
```

## Running

Save the example above to `app.py` and start the server:

```bash
python app.py
```

The application will be available at `http://localhost:8000/`.
