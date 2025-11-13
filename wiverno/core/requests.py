import json
from email.parser import BytesParser
from email.policy import default
from typing import Any
from urllib.parse import parse_qs, unquote


class QueryDict(dict):
    """
    A dictionary subclass for handling query string parameters with support for multiple values.

    Attributes:
        _list_data (dict[str, list[str]]): Internal storage for all parameter values.
    """

    def __init__(self, query_string: str = "") -> None:
        """
        Initialize a QueryDict from a query string.

        Args:
            query_string (str): URL query string to parse (without leading '?').
                               Empty values are preserved. Defaults to empty string.
        """
        super().__init__()
        self._list_data = {}

        if query_string:
            parsed = parse_qs(query_string, keep_blank_values=True)
            for key, values in parsed.items():
                self._list_data[key] = values
                super().__setitem__(key, values[0] if values else "")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get the first value for a given key.

        This method overrides dict.get() for clarity and consistency.
        Returns the first value if the key has multiple values.

        Args:
            key (str): The parameter name to retrieve.
            default (Any, optional): Default value if key not found. Defaults to None.

        Returns:
            Any: The first value associated with the key, or default if not found.
        """
        return super().get(key, default)

    def getlist(self, key: str, default: list[str] | None = None) -> list[str]:
        """
        Get all values for a given key as a list.

        Args:
            key (str): The parameter name to retrieve.
            default (list[str], optional): Default value if key not found.
                                          Defaults to empty list.

        Returns:
            list[str]: List of all values associated with the key, or default if not found.
        """
        return self._list_data.get(key, default or [])

    def __setitem__(self, key: str, value: Any) -> None:
        """
        Set a value for a given key, replacing any existing values.

        If a list is provided, stores all values but exposes only the first
        via dict interface. If a single value is provided, converts it to a list.

        Args:
            key (str): The parameter name to set.
            value (Any): The value(s) to set. Can be a single value or a list.
                        Single values are converted to strings and stored as a list.
        """
        if isinstance(value, list):
            self._list_data[key] = value
            super().__setitem__(key, value[0] if value else "")
        else:
            self._list_data[key] = [str(value)]
            super().__setitem__(key, str(value))


class ParseBody:
    """
    Handles parsing of POST request data from the WSGI environment.
    Supports: multipart/form-data, application/x-www-form-urlencoded, application/json.
    """

    @staticmethod
    def get_request_params(environ: dict[str, Any], raw_data: bytes) -> dict[str, Any]:
        """
        Parses POST request data from the WSGI environment.

        Args:
            environ (dict): The WSGI environment.
            raw_data (bytes): Raw POST body from wsgi.input.

        Returns:
            Dict[str, Any]: Parsed POST data.
        """
        content_type: str = environ.get("CONTENT_TYPE", "")

        if content_type.startswith("multipart/form-data") and "boundary=" in content_type:
            content: bytes = b"Content-Type: " + content_type.encode() + b"\r\n\r\n" + raw_data
            msg = BytesParser(policy=default).parsebytes(content)

            data: dict[str, Any] = {}
            if hasattr(msg, "iter_parts"):
                for part in msg.iter_parts():
                    name: str | None = part.get_param("name", header="content-disposition")
                    if name:
                        data[name] = part.get_content()
            return data

        if content_type == "application/x-www-form-urlencoded":
            return {k: v[0] for k, v in parse_qs(raw_data.decode()).items()}

        if content_type == "application/json":
            try:
                result: dict[str, Any] = json.loads(raw_data.decode())
                return result
            except json.JSONDecodeError:
                return {}

        return {}


class HeaderParser:
    """
    A utility class to parse headers from the WSGI environment.
    """

    @staticmethod
    def get_headers(environ: dict[str, Any]) -> dict[str, str]:
        """
        Parses headers from the WSGI environment.

        Args:
            environ (dict): The WSGI environment.

        Returns:
            dict: Parsed headers.
        """
        headers = {}
        for key, value in environ.items():
            if key.startswith("HTTP_"):
                header_name = key[5:].replace("_", "-").title()
                headers[header_name] = value
        return headers


class Request:
    """
    Represents an HTTP request with parsed data from the WSGI environment.

    Attributes:
        method (str): HTTP method (GET, POST, etc.).
        path (str): The request path.
        headers (Dict[str, str]): HTTP headers.
        query_params (QueryDict): Parsed query string parameters.
        data (Dict[str, Any]): Parsed request body.
        cookies (Dict[str, str]): Cookies from the request.
        content_type (str): Content-Type header value.
        content_length (int): Content-Length header value.
        client_ip (str): Client's IP address.
        server (str): Server name.
        user_agent (str): User-Agent header value.
        protocol (str): HTTP protocol version.
        scheme (str): URL scheme (http/https).
        is_secure (bool): Whether the connection is secure (HTTPS).
        path_params (Dict[str, Any]): URL path parameters extracted from dynamic routes.
    """

    method: str
    path: str
    headers: dict[str, str]
    query_params: QueryDict
    data: dict[str, Any]
    cookies: dict[str, str]
    content_type: str
    content_length: int
    client_ip: str
    server: str
    user_agent: str
    protocol: str
    scheme: str
    is_secure: bool
    path_params: dict[str, Any]

    def __init__(self, environ: dict[str, Any]) -> None:
        """
        Initializes a Request object from a WSGI environment.

        Args:
            environ (dict): The WSGI environment dictionary.
        """
        self.environ = environ

        self.method: str = environ.get("REQUEST_METHOD", "GET").upper()
        self.path: str = self._get_path()
        self.headers: dict[str, str] = HeaderParser.get_headers(environ)
        self.query_params: QueryDict = QueryDict(environ.get("QUERY_STRING", ""))
        self._raw_data = environ["wsgi.input"].read(self._parse_content_length())
        self.data = ParseBody.get_request_params(environ, self._raw_data)
        self.cookies: dict[str, str] = self._parse_cookies()
        self.content_type: str = environ.get("CONTENT_TYPE", "")
        self.content_length: int = self._parse_content_length()
        self.client_ip: str = environ.get("REMOTE_ADDR", "")
        self.server: str = environ.get("SERVER_NAME", "")
        self.user_agent: str = self.headers.get("User-Agent", "")
        self.protocol: str = environ.get("SERVER_PROTOCOL", "")
        self.scheme: str = environ.get("wsgi.url_scheme", "http")
        self.is_secure: bool = self.scheme == "https"
        self.path_params: dict[str, Any] = {}

    def _get_path(self) -> str:
        """
        Extracts and normalizes the request path from the WSGI environment.

        Returns:
            str: The normalized request path without trailing slash (except for root "/").
        """
        path: str = self.environ.get("PATH_INFO", "/")
        path = unquote(path)

        if not path:
            return "/"

        path = "/" + path.strip("/")

        if path != "/":
            path = path.rstrip("/")

        return path

    def _parse_content_length(self) -> int:
        """
        Parses the Content-Length header from the WSGI environment.

        Returns:
            int: The content length, or 0 if not present or invalid.
        """
        try:
            return int(self.environ.get("CONTENT_LENGTH", "0"))
        except (ValueError, TypeError):
            return 0

    def _parse_cookies(self) -> dict[str, str]:
        """
        Parses cookies from the HTTP_COOKIE header.

        Returns:
            Dict[str, str]: A dictionary mapping cookie names to their values.
        """
        cookie_str = self.environ.get("HTTP_COOKIE", "")
        cookies = {}
        for pair in cookie_str.split("; "):
            if "=" in pair:
                key, value = pair.split("=", 1)
                cookies[key] = value
        return cookies
