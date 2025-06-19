import json
from typing import Dict, Any, Optional
from urllib.parse import parse_qs, unquote
from email.parser import BytesParser
from email.policy import default

class ParseQuery:

    @staticmethod
    def parse_input_data(data: str) -> dict:
        """
        Parses the input data from a GET request query string into a dictionary.
        
        :param data: The query string from the GET request.
        :return: A dictionary with key-value pairs from the query string.
        """
        if not data:
            return {}
        
        # Split the query string into key-value pairs
        pairs = data.split('&')
        result = {}
        for pair in pairs:
            if '=' in pair:
                key, value = pair.split('=')
                result[key] = value
            else:
                result[pair] = None
        return result
    
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

    def get_request_params(self, environ: dict) -> Dict[str, Any]:
        """
        Parses POST request data from the WSGI environment.

        Args:
            environ (dict): The WSGI environment.

        Returns:
            dict: Parsed POST data.
        """
        content_type: str = environ.get('CONTENT_TYPE', '')
        content_length_str = environ.get('CONTENT_LENGTH', '0')
        try:
            content_length = int(content_length_str)
        except ValueError:
            content_length = 0
        wsgi_input: bytes = environ['wsgi.input'].read(content_length)

        if content_type.startswith('multipart/form-data'):
            boundary = content_type.split('boundary=')[-1]
            content: bytes = b'Content-Type: ' + content_type.encode() + b'\r\n\r\n' + wsgi_input
            msg = BytesParser(policy=default).parsebytes(content)

            data: Dict[str, Any] = {}
            for part in msg.iter_parts():
                name = part.get_param('name', header='content-disposition')
                if name:
                    data[name] = part.get_content()
            return data

        elif content_type == 'application/x-www-form-urlencoded':
            return {k: v[0] for k, v in parse_qs(wsgi_input.decode()).items()}

        elif content_type == 'application/json':
            return json.loads(wsgi_input.decode())

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
    
    def __init__(self, environ: dict):
        self.environ = environ

        self.method: str = environ.get("REQUEST_METHOD", "GET").upper()
        self.path: str = self._get_path()
        self.headers: Dict[str, str] = HeaderParser.get_headers(environ)
        self.query_params: Dict[str, Any] = ParseQuery.get_request_params(environ)
        self.data: Dict[str, Any] = ParseBody().get_request_params(environ)
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