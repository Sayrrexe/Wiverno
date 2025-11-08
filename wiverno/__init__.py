"""
Wiverno - A lightweight Python web framework
"""

try:
    from importlib.metadata import version

    __version__ = version("wiverno")
except ImportError:
    __version__ = "0.0.0-dev"
