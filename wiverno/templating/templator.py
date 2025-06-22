import os
from typing import Optional

from jinja2 import Environment, FileSystemLoader

_env: Optional[Environment] = None
_current_path: Optional[str] = None


def configure_environment(template_path: str = "templates") -> Environment:
    """Configure the Jinja2 environment for a specific template path."""
    global _env, _current_path
    base_dir = os.getcwd()
    _env = Environment(loader=FileSystemLoader(os.path.join(base_dir, template_path)))
    _current_path = template_path
    return _env


def reset_environment() -> None:
    """Reset the cached Jinja2 environment."""
    global _env, _current_path
    _env = None
    _current_path = None


def render(template_name: str, content: Optional[dict] = None, folder: str = "templates", **kwargs) -> str:
    """Render a template with the provided context."""
    global _env, _current_path
    if content is None:
        content = {}

    # Configure or reuse the environment for the requested folder
    if _env is None or folder != _current_path:
        configure_environment(folder)

    template = _env.get_template(template_name)
    if not template:
        raise FileNotFoundError(f"Template '{template_name}' not found in folder '{folder}'.")

    if content != {} and not isinstance(content, dict):
        raise TypeError("Content must be a dictionary.")

    return template.render(content, **kwargs)


# Initialize the environment with the default template folder
configure_environment("templates")

