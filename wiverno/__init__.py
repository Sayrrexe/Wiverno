"""
Wiverno - A lightweight Python web framework
"""

try:
    from importlib.metadata import version

    __version__ = version("wiverno")
except ImportError:
    __version__ = "0.0.0-dev"

from wiverno.core.requests import Request
from wiverno.core.routing.router import Router
from wiverno.main import Wiverno
from wiverno.templating.templator import Templator
from wiverno.views.base_views import BaseView

__all__ = [
    "BaseView",
    "Request",
    "Router",
    "Templator",
    "Wiverno",
]
