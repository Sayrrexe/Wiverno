import json
from typing import Dict, Any, Optional
from urllib.parse import parse_qs, unquote
from email.parser import BytesParser
from email.policy import default

class ParseQuery:

    @staticmethod
    def parse_input_data(data: str) -> Dict[str, str]:
        return {k: v[0] for k, v in parse_qs(data).items()}
    
    @staticmethod
    def get_request_params(environ: dict) -> dict:
        """
        Retrieves and parses the query string from the WSGI environment.
        
        :param environ: The WSGI environment dictionary.
        :return: A dictionary with parsed query parameters.
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
        path = self.environ.get("PATH_INFO", "/")
        return unquote(path if path.endswith("/") else path + "/")

    def _parse_content_length(self) -> int:
        try:
            return int(self.environ.get("CONTENT_LENGTH", "0"))
        except (ValueError, TypeError):
            return 0

    def _parse_cookies(self) -> Dict[str, str]:
        cookie_str = self.environ.get("HTTP_COOKIE", "")
        cookies = {}
        for pair in cookie_str.split("; "):
            if "=" in pair:
                key, value = pair.split("=", 1)
                cookies[key] = value
        return cookies