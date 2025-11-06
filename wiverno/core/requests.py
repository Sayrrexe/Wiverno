import json
from typing import Dict, Any, Optional
from urllib.parse import parse_qs, unquote
from email.parser import BytesParser
from email.policy import default

class ParseQuery:
    """
    Utility class for parsing query strings from URLs.
    """

    @staticmethod
    def parse_input_data(data: str) -> Dict[str, str]:
        """
        Parses a query string into a dictionary.

        Args:
            data (str): The query string to parse.

        Returns:
            Dict[str, str]: A dictionary mapping parameter names to their first values.
        """
        return {k: v[0] for k, v in parse_qs(data).items()}
    
    @staticmethod
    def get_request_params(environ: dict) -> dict:
        """
        Retrieves and parses the query string from the WSGI environment.

        Args:
            environ (dict): The WSGI environment dictionary.

        Returns:
            dict: A dictionary with parsed query parameters.
        """
        query_string = environ.get('QUERY_STRING', '')
        return ParseQuery.parse_input_data(query_string)
    
class ParseBody:
    """
    Handles parsing of POST request data from the WSGI environment.
    Supports: multipart/form-data, application/x-www-form-urlencoded, application/json.
    """
    
    @staticmethod
    def get_request_params(environ: dict, raw_data: bytes) -> Dict[str, Any]:
        """
        Parses POST request data from the WSGI environment.

        Args:
            environ (dict): The WSGI environment.
            raw_data (bytes): Raw POST body from wsgi.input.

        Returns:
            Dict[str, Any]: Parsed POST data.
        """
        content_type: str = environ.get('CONTENT_TYPE', '')

        if content_type.startswith('multipart/form-data') and 'boundary=' in content_type:
            boundary: str = content_type.split('boundary=')[-1]
            content: bytes = b'Content-Type: ' + content_type.encode() + b'\r\n\r\n' + raw_data
            msg = BytesParser(policy=default).parsebytes(content)

            data: Dict[str, Any] = {}
            for part in msg.iter_parts():
                name: Optional[str] = part.get_param('name', header='content-disposition')
                if name:
                    data[name] = part.get_content()
            return data

        elif content_type == 'application/x-www-form-urlencoded':
            return {k: v[0] for k, v in parse_qs(raw_data.decode()).items()}

        elif content_type == 'application/json':
            try:
                return json.loads(raw_data.decode())
            except json.JSONDecodeError:
                return {}

        return {}
    
class HeaderParser:
    """
    A utility class to parse headers from the WSGI environment.
    """

    @staticmethod
    def get_headers(environ: dict) -> Dict[str, str]:
        """
        Parses headers from the WSGI environment.

        Args:
            environ (dict): The WSGI environment.

        Returns:
            dict: Parsed headers.
        """
        headers = {}
        for key, value in environ.items():
            if key.startswith('HTTP_'):
                header_name = key[5:].replace('_', '-').title()
                headers[header_name] = value
        return headers
    
class Request:
    """
    Represents an HTTP request with parsed data from the WSGI environment.

    Attributes:
        method (str): HTTP method (GET, POST, etc.).
        path (str): The request path.
        headers (Dict[str, str]): HTTP headers.
        query_params (Dict[str, Any]): Parsed query string parameters.
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
    """
    method: str
    path: str
    headers: Dict[str, str]
    query_params: Dict[str, Any]
    data: Dict[str, Any]
    cookies: Dict[str, str]
    content_type: str
    content_length: int
    client_ip: str
    server: str
    user_agent: str
    protocol: str
    scheme: str
    is_secure: bool

    def __init__(self, environ: dict):
        """
        Initializes a Request object from a WSGI environment.

        Args:
            environ (dict): The WSGI environment dictionary.
        """
        self.environ = environ

        self.method: str = environ.get("REQUEST_METHOD", "GET").upper()
        self.path: str = self._get_path()
        self.headers: Dict[str, str] = HeaderParser.get_headers(environ)
        self.query_params: Dict[str, Any] = ParseQuery.get_request_params(environ)
        self._raw_data = environ['wsgi.input'].read(self._parse_content_length())
        self.data = ParseBody.get_request_params(environ, self._raw_data)
        self.cookies: Dict[str, str] = self._parse_cookies()
        self.content_type: str = environ.get("CONTENT_TYPE", "")
        self.content_length: int = self._parse_content_length()
        self.client_ip: str = environ.get("REMOTE_ADDR", "")
        self.server: str = environ.get("SERVER_NAME", "")
        self.user_agent: str = self.headers.get("User-Agent", "")
        self.protocol: str = environ.get("SERVER_PROTOCOL", "")
        self.scheme: str = environ.get("wsgi.url_scheme", "http")
        self.is_secure: bool = self.scheme == "https"
        
    def _get_path(self) -> str:
        """
        Extracts and normalizes the request path from the WSGI environment.

        Returns:
            str: The normalized request path with trailing slash.
        """
        path = self.environ.get("PATH_INFO", "/")
        return unquote(path if path.endswith("/") else path + "/")

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

    def _parse_cookies(self) -> Dict[str, str]:
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