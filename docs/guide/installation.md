# Installation

This guide will help you install Wiverno and set up your development environment.

## Requirements

Wiverno requires **Python 3.12 or higher**. Make sure you have a compatible Python version installed:

```bash
python --version
```

## Installation Methods

### Using pip (Recommended)

The easiest way to install Wiverno is using pip:

```bash
pip install wiverno
```

### From Source

To install the latest development version from GitHub:

```bash
git clone https://github.com/Sayrrexe/Wiverno.git
cd Wiverno
pip install .
```

### Development Installation

If you want to contribute to Wiverno or modify the source code, install in editable mode with development dependencies:

```bash
git clone https://github.com/Sayrrexe/Wiverno.git
cd Wiverno
pip install -e ".[dev]"
```

This will install Wiverno with all development tools including:

- pytest - for running tests
- ruff - for linting and formatting
- mypy - for type checking
- mkdocs-material - for building documentation
- and more...

### Using uv (Modern Alternative)

If you're using [uv](https://github.com/astral-sh/uv) for dependency management:

```bash
uv pip install wiverno
```

For development:

```bash
uv pip install -e ".[dev]"
```

## Virtual Environments

It's highly recommended to use a virtual environment to isolate your project dependencies.

### Using venv

```bash
# Create a virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate

# Activate it (Unix/macOS)
source venv/bin/activate

# Install Wiverno
pip install wiverno
```

### Using uv

```bash
# Create a virtual environment with uv
uv venv

# Activate it (Windows)
.venv\Scripts\activate

# Activate it (Unix/macOS)
source .venv/bin/activate

# Install Wiverno
uv pip install wiverno
```

## Verification

After installation, verify that Wiverno is installed correctly:

```bash
python -c "from wiverno.main import Wiverno; print('Wiverno imported successfully')"
```

You can also check the CLI tool:

```bash
wiverno help
```

## Optional Dependencies

Wiverno has minimal dependencies by default. The only required dependency is:

- **Jinja2** (>=3.1) - Template engine

Development dependencies (optional):

- **pytest** - Testing framework
- **pytest-cov** - Coverage reporting
- **pytest-benchmark** - Performance benchmarking
- **ruff** - Linting and formatting
- **mypy** - Static type checking
- **mkdocs-material** - Documentation
- **rich** - Terminal formatting
- **watchdog** - File watching for auto-reload

## Troubleshooting

### Python Version Issues

If you get an error about Python version:

```
ERROR: Package 'wiverno' requires a different Python: 3.11.0 not in '>=3.12'
```

You need to upgrade to Python 3.12 or higher. Download the latest version from [python.org](https://www.python.org/downloads/).

### Permission Errors

If you get permission errors during installation, try:

```bash
pip install --user wiverno
```

Or use a virtual environment (recommended).

### Import Errors

If you can't import Wiverno after installation:

1. Make sure you're in the correct virtual environment
2. Check that the installation completed successfully
3. Try reinstalling: `pip install --force-reinstall wiverno`

## Next Steps

Now that you have Wiverno installed, head over to the [Quickstart](quickstart.md) guide to create your first application!
