import contextlib
import re
from dataclasses import dataclass
from re import Pattern
from typing import Any


@dataclass(frozen=True)
class PathPattern:
    """
    Represents a compiled path pattern for dynamic route matching.

    A path pattern is created from a path template like "/users/{id:int}"
    and contains the compiled regex pattern, parameter names, type converters,
    and metadata for efficient matching and sorting.

    Attributes:
        pattern: Compiled regex pattern for matching paths.
        pattern_str: Original path template string (e.g., "/users/{id:int}").
        param_names: Tuple of parameter names in order of appearance.
        converters: Dictionary mapping parameter names to their type converters.
        segments_count: Number of path segments (for priority sorting).
    """

    pattern: Pattern[str]
    pattern_str: str
    param_names: tuple[str, ...]
    converters: dict[str, type]
    segments_count: int

    def match(self, path: str) -> dict[str, Any] | None:
        """
        Match a path against this pattern and extract parameters.

        Args:
            path: The URL path to match.

        Returns:
            A dictionary of parameter names to converted values if the path matches,
            or None if no match.
        """
        match = self.pattern.match(path)
        if not match:
            return None

        params = match.groupdict()

        for name, value in params.items():
            if name in self.converters:
                with contextlib.suppress(ValueError, TypeError):
                    params[name] = self.converters[name](value)

        return params

    def with_prefix(self, prefix: str) -> "PathPattern":
        """
        Create a new PathPattern with a prefix prepended to the path.

        Args:
            prefix: The prefix to add (e.g., "/api").

        Returns:
            A new PathPattern with the prefix applied.
        """
        new_pattern_str = prefix + self.pattern_str
        return compile_path(new_pattern_str)


def compile_path(path: str) -> PathPattern:
    """
    Compile a path template into a PathPattern for matching.

    Supports FastAPI-style parameter syntax:
    - {name} - String parameter
    - {name:int} - Integer parameter
    - {name:float} - Float parameter
    - {name:str} - String parameter (explicit)
    - {name:path} - Path parameter (matches slashes)

    Args:
        path: The path template to compile (e.g., "/users/{id:int}").

    Returns:
        A compiled PathPattern ready for matching.

    Raises:
        ValueError: If the path contains too many parameters (ReDoS protection).
    """
    # ReDoS protection: limit number of parameters
    param_count = path.count("{")
    if param_count > 20:
        raise ValueError(f"Too many parameters in path: {param_count} (max 20)")

    param_names = []
    converters = {}
    segments_count = path.count("/")

    # FastAPI style: {name} or {name:type}
    def replace_fastapi_param(match: re.Match[str]) -> str:
        content = match.group(1)

        if ":" in content:
            name, type_str = content.split(":", 1)
        else:
            name = content
            type_str = "str"

        param_names.append(name)

        type_map = {
            "int": (int, r"[0-9]+"),
            "float": (float, r"[0-9]+\.?[0-9]*"),
            "str": (str, r"[^/]+"),
            "path": (str, r".+"),
        }

        converter, regex = type_map.get(type_str, (str, r"[^/]+"))
        converters[name] = converter

        return f"(?P<{name}>{regex})"

    pattern_str = re.sub(r"\{([^}]+)\}", replace_fastapi_param, path)

    pattern_str = f"^{pattern_str}$"

    return PathPattern(
        pattern=re.compile(pattern_str),
        pattern_str=path,
        param_names=tuple(param_names),
        converters=converters,
        segments_count=segments_count,
    )
